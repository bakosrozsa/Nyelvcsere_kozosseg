<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '../config/api'

const sessions = ref([])
const mentors = ref([])
const currentUser = ref(null)
const loading = ref(false)
const error = ref('')
const minDateTime = ref('')
const participantsBySession = ref({})
const evaluationsBySession = ref({})
const evaluationForms = ref({})
const evaluationSaving = ref({})
const myEvaluationBySession = ref({})
const sessionTimeForms = ref({})
const availableGroupSessions = ref([])
const groupLoading = ref(false)
const joiningGroup = ref({})
const leavingGroup = ref({})

const newSession = ref({
  mentor_profile_id: '',
  scheduled_time: '',
  max_students: '',
})

const mentorByProfileId = computed(() => {
  const map = new Map()
  mentors.value.forEach((mentor) => {
    map.set(String(mentor.id), mentor)
  })
  return map
})

const visibleMentors = computed(() => {
  if (currentUser.value?.role !== 'mentor') {
    return mentors.value
  }

  return mentors.value.filter((mentor) => String(mentor.userId) !== String(currentUser.value.id))
})

const isMentor = computed(() => currentUser.value?.role === 'mentor')
const ownMentorProfile = computed(() => {
  if (!currentUser.value) {
    return null
  }
  return mentors.value.find((mentor) => String(mentor.userId) === String(currentUser.value.id)) || null
})

const getCurrentDateTimeLocal = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

const toDateTimeLocalValue = (value) => {
  if (!value) {
    return ''
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return ''
  }

  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

const getHeaders = () => {
  const token = localStorage.getItem('token')
  return { Authorization: `Bearer ${token}` }
}

const fetchCurrentUser = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/users/me`, { headers: getHeaders() })
    currentUser.value = response.data
  } catch (err) {
    currentUser.value = null
    console.error(err)
  }
}

const fetchMentors = async () => {
  error.value = ''
  try {
    const headers = getHeaders()
    const [profilesRes, usersRes, languagesRes] = await Promise.all([
      axios.get(`${API_BASE_URL}/mentor-profiles`, { headers }),
      axios.get(`${API_BASE_URL}/public/mentor-users`, { headers }),
      axios.get(`${API_BASE_URL}/languages`, { headers }),
    ])

    const usersById = new Map(usersRes.data.map((u) => [u.id, u]))
    const languagesById = new Map(languagesRes.data.map((l) => [l.id, l]))

    mentors.value = profilesRes.data
      .map((profile) => {
        const user = usersById.get(profile.user_id)
        if (!user) return null
        return {
          id: profile.id,
          userId: user.id,
          name: user.name,
          email: user.email,
          teachesLanguage: languagesById.get(profile.offered_language_id)?.name || 'Nincs megadva',
        }
      })
      .filter(Boolean)

    const selectableMentors = visibleMentors.value
    if (!newSession.value.mentor_profile_id && selectableMentors.length > 0) {
      newSession.value.mentor_profile_id = String(selectableMentors[0].id)
    }
  } catch (err) {
    error.value = 'Hiba a mentorok lekérésekor.'
    console.error(err)
  }
}

const fetchSessions = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get(`${API_BASE_URL}/sessions`, { headers: getHeaders() })
    sessions.value = response.data
    sessionTimeForms.value = response.data.reduce((acc, session) => {
      acc[session.id] = toDateTimeLocalValue(session.scheduled_time)
      return acc
    }, {})
    await fetchSessionDetailsForSessions()
  } catch (err) {
    error.value = 'Hiba a foglalkozások lekérésekor.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const fetchAvailableGroupSessions = async () => {
  if (currentUser.value?.role !== 'student') {
    availableGroupSessions.value = []
    return
  }

  groupLoading.value = true
  try {
    const response = await axios.get(`${API_BASE_URL}/sessions/group-available`, { headers: getHeaders() })
    availableGroupSessions.value = response.data
  } catch (err) {
    console.error(err)
    availableGroupSessions.value = []
  } finally {
    groupLoading.value = false
  }
}

const fetchSessionDetailsForSessions = async () => {
  const nextParticipants = {}
  const nextEvaluations = {}
  const nextForms = {}
  const nextMyEvaluations = {}

  await Promise.all(
    sessions.value.map(async (session) => {
      const requests = [
        axios.get(`${API_BASE_URL}/sessions/${session.id}/participants`, { headers: getHeaders() }),
        axios.get(`${API_BASE_URL}/sessions/${session.id}/evaluations`, { headers: getHeaders() }),
      ]

      if (!isMentor.value) {
        requests.push(axios.get(`${API_BASE_URL}/sessions/${session.id}/progress-log`, { headers: getHeaders() }))
      }

      const requestResults = await Promise.allSettled(requests)
      const participantsResult = requestResults[0]
      const evaluationsResult = requestResults[1]
      const progressLogResult = requestResults[2]

      const participants = participantsResult.status === 'fulfilled' ? (participantsResult.value.data || []) : []
      const evaluations = evaluationsResult.status === 'fulfilled' ? (evaluationsResult.value.data || []) : []
      const progressLog = progressLogResult?.status === 'fulfilled' ? (progressLogResult.value.data || null) : null

      nextParticipants[session.id] = participants
      nextEvaluations[session.id] = evaluations

      if (isMentor.value) {
        const formMap = {}
        participants.forEach((participant) => {
          const existing = evaluations.find((evaluation) => evaluation.student_id === participant.student_id)
          formMap[participant.student_id] = {
            notes: existing?.notes || '',
            rating: existing?.rating ? String(existing.rating) : '',
          }
        })
        nextForms[session.id] = formMap
      }

      if (!isMentor.value) {
        const myEvaluation = evaluations.find(
          (evaluation) => String(evaluation.student_id) === String(currentUser.value?.id)
        ) || progressLog || null
        nextMyEvaluations[session.id] = myEvaluation
      }
    })
  )

  participantsBySession.value = nextParticipants
  evaluationsBySession.value = nextEvaluations
  evaluationForms.value = nextForms
  myEvaluationBySession.value = nextMyEvaluations
}

const canRateSession = (session) => session?.status === 'completed'
const canWriteNotes = (session) => session?.status === 'completed'
const canShowFeedbackSummary = (session) => isMentor.value || session?.status !== 'canceled'
const participantsCount = (sessionId) => participantsBySession.value[sessionId]?.length || 0
const canStudentDeleteSession = (session) => {
  if (currentUser.value?.role !== 'student') {
    return false
  }
  return session?.status === 'scheduled' && !session?.is_group && String(session?.student_id) === String(currentUser.value.id)
}
const canStudentLeaveGroup = (session) => {
  if (currentUser.value?.role !== 'student') {
    return false
  }
  if (session?.status !== 'scheduled' || !session?.is_group) {
    return false
  }
  return (participantsBySession.value[session.id] || []).some(
    (student) => String(student.student_id) === String(currentUser.value.id)
  )
}
const hasStudentSessionActions = (session) => canStudentDeleteSession(session) || canStudentLeaveGroup(session)

const canEditSessionTime = (session) => {
  if (!currentUser.value) {
    return false
  }

  if (session.status !== 'scheduled') {
    return false
  }

  return currentUser.value.role === 'mentor' || currentUser.value.id === session.student_id
}

watch(
  [currentUser, mentors],
  () => {
    if (currentUser.value?.role !== 'mentor') {
      return
    }

    const ownMentorProfile = mentors.value.find((mentor) => mentor.userId === currentUser.value.id)
    if (!ownMentorProfile) {
      return
    }

    if (String(newSession.value.mentor_profile_id) === String(ownMentorProfile.id)) {
      newSession.value.mentor_profile_id = visibleMentors.value[0] ? String(visibleMentors.value[0].id) : ''
    }
  },
  { immediate: true }
)

const createSession = async () => {
  if (!newSession.value.scheduled_time) return

  if (!isMentor.value && !newSession.value.mentor_profile_id) return
  if (isMentor.value && !ownMentorProfile.value) {
    alert('Nincs elerheto mentor profil a csoportos foglalkozashoz.')
    return
  }

  minDateTime.value = getCurrentDateTimeLocal()
  const selectedDate = new Date(newSession.value.scheduled_time)
  if (Number.isNaN(selectedDate.getTime()) || selectedDate.getTime() < Date.now()) {
    alert('A jelenlegi időpontnál korábbra nem lehet foglalni.')
    return
  }

  try {
    const isGroup = isMentor.value
    const payload = {
      mentor_profile_id: Number(isGroup ? ownMentorProfile.value.id : newSession.value.mentor_profile_id),
      scheduled_time: new Date(newSession.value.scheduled_time).toISOString(),
      is_group: isGroup,
      max_students: isGroup ? Number(newSession.value.max_students) : null,
    }

    if (isGroup && (!payload.max_students || payload.max_students < 2 || payload.max_students > 10)) {
      alert('Csoportos foglalkozashoz 2 es 10 fo kozotti limitet adj meg.')
      return
    }

    await axios.post(`${API_BASE_URL}/sessions`, payload, { headers: getHeaders() })

    fetchSessions()
    fetchAvailableGroupSessions()
    newSession.value.scheduled_time = ''
    if (isGroup) {
      newSession.value.max_students = ''
      alert('Sikeres csoportos foglalkozas letrehozva!')
    } else {
      alert('Sikeres időpontfoglalás!')
    }
  } catch (err) {
    const apiMessage = err?.response?.data?.detail
    alert(apiMessage || 'Hiba történt a létrehozás során.')
    console.error(err)
  }
}

const joinGroupSession = async (groupSessionId) => {
  joiningGroup.value = { ...joiningGroup.value, [groupSessionId]: true }
  try {
    await axios.post(`${API_BASE_URL}/sessions/${groupSessionId}/join`, null, { headers: getHeaders() })
    await Promise.all([fetchSessions(), fetchAvailableGroupSessions()])
    alert('Sikeres jelentkezes a csoportos foglalkozasra!')
  } catch (err) {
    alert(err?.response?.data?.detail || 'Nem sikerult jelentkezni a csoportos foglalkozasra.')
    console.error(err)
  } finally {
    joiningGroup.value = { ...joiningGroup.value, [groupSessionId]: false }
  }
}

const leaveGroupSession = async (groupSessionId) => {
  const confirmed = window.confirm('Biztosan lejelentkezel a csoportos foglalkozasrol?')
  if (!confirmed) {
    return
  }

  leavingGroup.value = { ...leavingGroup.value, [groupSessionId]: true }
  try {
    await axios.delete(`${API_BASE_URL}/sessions/${groupSessionId}/leave`, { headers: getHeaders() })
    await Promise.all([fetchSessions(), fetchAvailableGroupSessions()])
    alert('Sikeres lejelentkezes a csoportos foglalkozasrol.')
  } catch (err) {
    alert(err?.response?.data?.detail || 'Nem sikerult lejelentkezni a csoportos foglalkozasrol.')
    console.error(err)
  } finally {
    leavingGroup.value = { ...leavingGroup.value, [groupSessionId]: false }
  }
}

const updateSessionStatus = async (sessionId, newStatus) => {
  const isFinalStatus = newStatus === 'completed' || newStatus === 'canceled'
  if (isFinalStatus) {
    const confirmed = window.confirm(
      newStatus === 'completed'
        ? 'Biztosan befejezettre állítod ezt a foglalkozást?'
        : 'Biztosan lemondod ezt a foglalkozást?'
    )
    if (!confirmed) {
      return
    }
  }

  try {
    await axios.put(`${API_BASE_URL}/sessions/${sessionId}`, { status: newStatus }, { headers: getHeaders() })
    fetchSessions()
  } catch (err) {
    alert('Hiba történt a módosítás során.')
    console.error(err)
  }
}

const updateSessionTime = async (sessionId) => {
  const scheduledTime = sessionTimeForms.value[sessionId]
  if (!scheduledTime) {
    return
  }

  const selectedDate = new Date(scheduledTime)
  if (Number.isNaN(selectedDate.getTime()) || selectedDate.getTime() < Date.now()) {
    alert('A jelenlegi időpontnál korábbra nem lehet módosítani.')
    return
  }

  try {
    await axios.put(
      `${API_BASE_URL}/sessions/${sessionId}`,
      { scheduled_time: new Date(scheduledTime).toISOString() },
      { headers: getHeaders() }
    )
    fetchSessions()
  } catch (err) {
    alert(err?.response?.data?.detail || 'Hiba történt az időpont módosításakor.')
    console.error(err)
  }
}

const deleteSession = async (sessionId) => {
  if (!confirm('Biztosan törölni szeretnéd ezt a foglalkozást?')) return

  try {
    await axios.delete(`${API_BASE_URL}/sessions/${sessionId}`, { headers: getHeaders() })
    fetchSessions()
  } catch (err) {
    alert('Hiba történt a törlés során.')
    console.error(err)
  }
}

const saveStudentEvaluation = async (session, student) => {
  const sessionId = session.id
  const form = evaluationForms.value?.[sessionId]?.[student.student_id] || { notes: '', rating: '' }
  const saveKey = `${sessionId}:${student.student_id}`
  evaluationSaving.value = { ...evaluationSaving.value, [saveKey]: true }

  try {
    if (!canWriteNotes(session) && form.notes?.trim()) {
      alert('Megjegyzést csak befejezett foglalkozáshoz adhatsz meg.')
      return
    }

    const payload = {
      notes: canWriteNotes(session) ? form.notes?.trim() || null : null,
    }

    if (canRateSession(session)) {
      payload.rating = form.rating ? Number(form.rating) : null
    } else if (form.rating) {
      alert('Értékelést csak befejezett foglalkozáshoz adhatsz meg.')
      return
    }

    await axios.put(
      `${API_BASE_URL}/sessions/${sessionId}/evaluations/${student.student_id}`,
      payload,
      { headers: getHeaders() }
    )

    await fetchSessionDetailsForSessions()
    alert('Előrehaladás mentve.')
  } catch (err) {
    alert('Hiba történt az előrehaladás mentésekor.')
    console.error(err)
  } finally {
    evaluationSaving.value = { ...evaluationSaving.value, [saveKey]: false }
  }
}

onMounted(() => {
  minDateTime.value = getCurrentDateTimeLocal()
  Promise.all([fetchCurrentUser(), fetchMentors()]).then(() => {
    if (currentUser.value?.role === 'mentor' && currentUser.value.id) {
      const ownMentorProfile = mentors.value.find((mentor) => mentor.userId === currentUser.value.id)
      if (ownMentorProfile && String(newSession.value.mentor_profile_id) === String(ownMentorProfile.id)) {
        newSession.value.mentor_profile_id = ''
      }
    }
    if (!newSession.value.mentor_profile_id && visibleMentors.value.length > 0) {
      newSession.value.mentor_profile_id = String(visibleMentors.value[0].id)
    }
    fetchSessions()
    fetchAvailableGroupSessions()
  })
})
</script>

<template>
  <div class="sessions-page">
    <h2>Foglalkozások</h2>

    <div v-if="error" class="error-box">{{ error }}</div>

    <div class="create-box">
      <h3>{{ isMentor ? 'Csoportos foglalkozás létrehozása' : 'Új időpont foglalása' }}</h3>
      <form @submit.prevent="createSession" class="inline-form">
        <div v-if="!isMentor">
          <label>Mentor:</label>
          <select v-model="newSession.mentor_profile_id" required class="input">
            <option value="" disabled>Válassz mentort</option>
            <option v-for="mentor in visibleMentors" :key="mentor.id" :value="String(mentor.id)">
              {{ mentor.name }}
            </option>
          </select>
        </div>
        <div v-else>
          <label>Tanuló limit:</label>
          <input type="number" min="2" max="10" v-model="newSession.max_students" required class="input" />
        </div>
        <div>
          <label>Időpont:</label>
          <input type="datetime-local" v-model="newSession.scheduled_time" :min="minDateTime" required class="input" />
        </div>
        <button type="submit" class="btn btn-primary">{{ isMentor ? 'Csoport létrehozása' : 'Létrehozás' }}</button>
      </form>
    </div>

    <div v-if="!isMentor" class="group-box">
      <h3>Elérhető csoportos foglalkozások</h3>
      <p v-if="groupLoading">Csoportos alkalmak betöltése...</p>
      <p v-else-if="availableGroupSessions.length === 0">Jelenleg nincs szabad csoportos alkalom.</p>
      <div v-else class="group-list">
        <article v-for="group in availableGroupSessions" :key="group.id" class="group-item">
          <p><strong>Mentor:</strong> {{ mentorByProfileId.get(String(group.mentor_profile_id))?.name || `Profil ID: ${group.mentor_profile_id}` }}</p>
          <p><strong>Időpont:</strong> {{ new Date(group.scheduled_time).toLocaleString('hu-HU') }}</p>
          <p><strong>Limit:</strong> {{ group.participants_count }}/{{ group.max_students }}</p>
          <button class="btn btn-primary" :disabled="joiningGroup[group.id]" @click="joinGroupSession(group.id)">
            {{ joiningGroup[group.id] ? 'Jelentkezés...' : 'Jelentkezem' }}
          </button>
        </article>
      </div>
    </div>

    <div v-if="loading">Betöltés...</div>

    <div v-else class="sessions-list">
      <h3>Jelenlegi foglalások</h3>
      <p v-if="sessions.length === 0">Még nincs egyetlen foglalkozás sem.</p>

      <div v-for="session in sessions" :key="session.id" class="session-card">
        <div class="session-info">
          <p>
            <strong>Mentor:</strong>
            {{ mentorByProfileId.get(String(session.mentor_profile_id))?.name || `Profil ID: ${session.mentor_profile_id}` }}
          </p>
          <p><strong>Időpont:</strong> {{ new Date(session.scheduled_time).toLocaleString('hu-HU') }}</p>
          <p>
            <strong>Státusz:</strong>
            <span :class="['status-badge', session.status]">{{ session.status }}</span>
          </p>
          <p v-if="session.is_group">
            <strong>Résztvevők:</strong>
            {{ participantsCount(session.id) }}/{{ session.max_students }}
          </p>

          <div v-if="session.is_group && participantsBySession[session.id]?.length" class="participants-box">
            <h4>Feljelentkezett tanulók</h4>
            <ul class="participants-list">
              <li v-for="student in participantsBySession[session.id]" :key="student.student_id">
                {{ student.student_name }} ({{ student.student_email }})
              </li>
            </ul>
          </div>

          <div v-if="!isMentor && canShowFeedbackSummary(session)" class="student-feedback-box">
            <p>
              <strong>Értékelés:</strong>
              {{ myEvaluationBySession[session.id]?.rating ? `${myEvaluationBySession[session.id].rating}/5` : 'Még nincs értékelés' }}
            </p>
            <p v-if="myEvaluationBySession[session.id]?.notes">
              <strong>Megjegyzés:</strong>
              {{ myEvaluationBySession[session.id].notes }}
            </p>
          </div>

          <div v-if="canEditSessionTime(session)" class="time-editor">
            <h4>Időpont módosítása</h4>
            <label :for="`time-${session.id}`">Új időpont</label>
            <input
              :id="`time-${session.id}`"
              v-model="sessionTimeForms[session.id]"
              type="datetime-local"
              class="input"
              :min="minDateTime"
            />
            <button class="btn btn-primary" @click="updateSessionTime(session.id)">Időpont mentése</button>
          </div>

          <div v-if="isMentor && canRateSession(session)" class="progress-editor">
            <h4>Tanulónkénti értékelés</h4>
            <p v-if="!participantsBySession[session.id]?.length">Ehhez a foglalkozáshoz nincs tanuló.</p>

            <div
              v-for="student in participantsBySession[session.id] || []"
              :key="student.student_id"
              class="student-evaluation-card"
            >
              <h5>{{ student.student_name }}</h5>

              <div v-if="evaluationForms[session.id]?.[student.student_id]" class="evaluation-fields">
                <div class="field-group">
                  <label :for="`rating-${session.id}-${student.student_id}`">Értékelés (1–5)</label>
                  <select
                    :id="`rating-${session.id}-${student.student_id}`"
                    v-model="evaluationForms[session.id][student.student_id].rating"
                    class="input"
                  >
                    <option value="">Nincs értékelés</option>
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                    <option value="4">4</option>
                    <option value="5">5</option>
                  </select>
                </div>

                <div class="field-group">
                  <label :for="`notes-${session.id}-${student.student_id}`">Megjegyzés</label>
                  <textarea
                    :id="`notes-${session.id}-${student.student_id}`"
                    v-model="evaluationForms[session.id][student.student_id].notes"
                    class="input notes-input"
                    rows="3"
                    placeholder="Mit gyakoroltatok, miben fejlődött a tanuló?"
                  />
                </div>

                <button
                  class="btn btn-primary btn-save"
                  :disabled="evaluationSaving[`${session.id}:${student.student_id}`]"
                  @click="saveStudentEvaluation(session, student)"
                >
                  {{ evaluationSaving[`${session.id}:${student.student_id}`] ? 'Mentés...' : 'Értékelés mentése' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="isMentor && session.status === 'scheduled'" class="session-actions">
          <button @click="updateSessionStatus(session.id, 'completed')" class="btn btn-success">
            Befejezettre állít
          </button>
          <button @click="updateSessionStatus(session.id, 'canceled')" class="btn btn-warning">
            Lemondás
          </button>
          <button @click="deleteSession(session.id)" class="btn btn-danger">Törlés</button>
        </div>

        <div v-else-if="hasStudentSessionActions(session)" class="session-actions">
          <button
            v-if="canStudentLeaveGroup(session)"
            @click="leaveGroupSession(session.id)"
            class="btn btn-warning"
            :disabled="leavingGroup[session.id]"
          >
            {{ leavingGroup[session.id] ? 'Lejelentkezes...' : 'Lejelentkezes' }}
          </button>
          <button
            v-if="canStudentDeleteSession(session)"
            @click="deleteSession(session.id)"
            class="btn btn-danger"
          >
            Törlés
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sessions-page { padding: 20px; max-width: 900px; margin: 0 auto; }
h2 { color: #f1f5f9; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 10px; }

.error-box { background: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; margin-bottom: 20px; }

.create-box { background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 8px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3); margin-bottom: 30px; }
.group-box { background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 8px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3); margin-bottom: 30px; }
.inline-form { display: flex; gap: 15px; align-items: flex-end; }
.input { padding: 8px 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 0.92rem; width: 100%; box-sizing: border-box; }
.input:focus { outline: none; border-color: #1f67c8; box-shadow: 0 0 0 3px rgba(31, 103, 200, 0.12); }

.group-list { display: grid; gap: 10px; }
.group-item { border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 8px; padding: 10px 12px; background: rgba(99, 102, 241, 0.08); }
.group-item p { margin: 6px 0; color: #f1f5f9; }

.participants-box { margin-top: 10px; padding: 10px; border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 8px; background: rgba(99, 102, 241, 0.08); text-align: left; }
.participants-box h4 { margin: 0; font-size: 0.95rem; color: #f1f5f9; }
.participants-list { margin: 8px 0 0; padding-left: 18px; }
.student-feedback-box { margin-top: 10px; }

.session-card { background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 15px; display: flex; flex-direction: column; align-items: center; text-align: center; gap: 14px; }
.session-info { width: 100%; }
.session-info p { margin: 5px 0; color: #cbd5e1; }

/* Progress / evaluation editor */
.progress-editor {
  margin-top: 12px;
  padding: 14px 16px;
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: 10px;
}
.progress-editor h4 {
  margin: 0 0 12px;
  color: #f1f5f9;
  font-size: 0.95rem;
}

/* Individual student evaluation card */
.student-evaluation-card {
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: 8px;
  background: rgba(99, 102, 241, 0.08);
  padding: 14px 16px;
  margin-top: 10px;
  text-align: left;
}
.student-evaluation-card h5 {
  margin: 0 0 12px;
  font-size: 0.95rem;
  color: #f1f5f9;
  border-bottom: 1px solid rgba(99, 102, 241, 0.25);
  padding-bottom: 8px;
}

/* Stacked fields layout */
.evaluation-fields {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.field-group label {
  font-size: 0.82rem;
  font-weight: 600;
  color: #cbd5e1;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.field-group select.input {
  max-width: 180px;
}

.notes-input {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.btn-save {
  align-self: flex-start;
  margin-top: 4px;
}

/* Time editor */
.time-editor {
  margin-top: 12px;
  padding: 14px 16px;
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: 10px;
  display: grid;
  gap: 8px;
  text-align: left;
}
.time-editor h4 { margin: 0 0 2px; color: #f1f5f9; font-size: 0.95rem; }
.time-editor label { font-size: 0.82rem; font-weight: 600; color: #cbd5e1; text-transform: uppercase; letter-spacing: 0.04em; }

.status-badge { padding: 3px 8px; border-radius: 12px; font-size: 0.85rem; font-weight: bold; }
.status-badge.scheduled { background: rgba(99, 102, 241, 0.25); color: #818cf8; }
.status-badge.completed { background: rgba(34, 197, 94, 0.25); color: #86efac; }
.status-badge.canceled { background: rgba(251, 146, 60, 0.25); color: #fdba74; }

.session-actions { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }
.btn { padding: 8px 14px; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 0.88rem; transition: opacity 0.2s, box-shadow 0.2s; }
.btn:hover { opacity: 0.85; box-shadow: 0 2px 6px rgba(0,0,0,0.12); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: #4f46e5; color: white; }
.btn-success { background: #22c55e; color: white; }
.btn-warning { background: #f59e0b; color: white; }
.btn-danger { background: #ef4444; color: white; }
</style>