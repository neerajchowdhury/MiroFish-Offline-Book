const STORAGE_KEY = 'mirofish_swarmbook_session'

export function createDefaultSwarmbookSession() {
  return {
    projectId: '',
    project: null,
    manuscript: {
      text: '',
      filename: '',
      language: '',
    },
    metadata: {
      projectName: '',
      authorName: '',
      bookType: 'fiction',
      genre: '',
      targetReader: '',
      title: '',
      subtitle: '',
      blurb: '',
      compTitles: '',
      coverBrief: '',
      privacyMode: 'local_only',
    },
    evidencePack: null,
    simulationConfig: {
      personaCount: 12,
      platforms: ['goodreads', 'reddit', 'booktok'],
      privacyMode: 'local_only',
      simulationSeed: 17,
    },
    simulationRun: null,
    report: null,
    comparison: null,
    personaChat: {
      personaId: '',
      question: '',
      response: null,
    },
  }
}

export function getSwarmbookSession() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) {
      return createDefaultSwarmbookSession()
    }
    return { ...createDefaultSwarmbookSession(), ...JSON.parse(raw) }
  } catch (error) {
    console.warn('Failed to read Swarmbook session:', error)
    return createDefaultSwarmbookSession()
  }
}

export function saveSwarmbookSession(session) {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session))
}

export function updateSwarmbookSession(patch) {
  const current = getSwarmbookSession()
  const next = {
    ...current,
    ...patch,
    manuscript: {
      ...current.manuscript,
      ...(patch.manuscript || {}),
    },
    metadata: {
      ...current.metadata,
      ...(patch.metadata || {}),
    },
    simulationConfig: {
      ...current.simulationConfig,
      ...(patch.simulationConfig || {}),
    },
    personaChat: {
      ...current.personaChat,
      ...(patch.personaChat || {}),
    },
  }
  saveSwarmbookSession(next)
  return next
}

export function clearSwarmbookSession() {
  window.localStorage.removeItem(STORAGE_KEY)
}
