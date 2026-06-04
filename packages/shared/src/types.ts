import type { Mood, Tense, Person } from "./enums"

export type ConjugationEntry = {
  mood:        Mood
  tense:       Tense
  person:      Person
  form:        string
  isIrregular: boolean
  ruleCode:    string | null
  noteEn:      string | null
  noteDe:      string | null
}

// Full verb returned by GET /verbs/:id
export type VerbDetail = {
  id:             string
  infinitive:     string
  translationsEn: string[]
  translationsDe: string[]
  gerund:         string
  pastParticiple: string
  isReflexive:    boolean
  cefrLevel:      string
  thematicGroup:  string
  tags:           string[]
  conjugations:   ConjugationEntry[]
}

// Lightweight verb returned by GET /verbs/random (no conjugations)
export type VerbSummary = Omit<VerbDetail, "conjugations">

// User progress stored in localStorage
export type VerbHistory = {
  correct:   number
  incorrect: number
  lastSeen:  number // timestamp ms
}

export type UserProgress = {
  language:    "de" | "en"
  streak:      number
  lastSeenDate: string // ISO date
  verbHistory: Record<string, VerbHistory> // keyed by verbId
}
