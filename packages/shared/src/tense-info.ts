import { Mood, Tense } from "./enums"

export type TenseInfo = {
  mood:        Mood
  tense:       Tense
  nameEn:      string
  nameDe:      string
  spanishName: string
  usageEn:     string
  usageDe:     string
}

export const TENSE_INFO: TenseInfo[] = [
  // ── Indicativo ──────────────────────────────────────────────────────────────
  {
    mood: Mood.INDICATIVO, tense: Tense.PRESENTE,
    nameEn: "Simple Present", nameDe: "Präsens", spanishName: "Presente de Indicativo",
    usageEn: "Used for current actions, habits, and universal truths. Also used for the near future with a time expression.",
    usageDe: "Für gegenwärtige Handlungen, Gewohnheiten und allgemeine Wahrheiten. Auch für die nahe Zukunft mit Zeitangabe.",
  },
  {
    mood: Mood.INDICATIVO, tense: Tense.PRETERITO_INDEFINIDO,
    nameEn: "Simple Past", nameDe: "Indefinido / Perfecto Simple", spanishName: "Pretérito Indefinido",
    usageEn: "For completed past actions with a clear endpoint, often with specific time markers (ayer, en 2010, una vez).",
    usageDe: "Für abgeschlossene Vergangenheitshandlungen mit klarem Endpunkt, oft mit konkreten Zeitangaben (ayer, en 2010).",
  },
  {
    mood: Mood.INDICATIVO, tense: Tense.PRETERITO_IMPERFECTO,
    nameEn: "Imperfect Past", nameDe: "Imperfekt / Imperfecto", spanishName: "Pretérito Imperfecto",
    usageEn: "For ongoing or habitual past actions, background descriptions, and states of being in the past.",
    usageDe: "Für andauernde oder gewohnheitsmäßige Vergangenheitshandlungen, Hintergrundbeschreibungen und Zustände in der Vergangenheit.",
  },
  {
    mood: Mood.INDICATIVO, tense: Tense.PRETERITO_PERFECTO_COMPUESTO,
    nameEn: "Present Perfect", nameDe: "Perfekt / Pretérito Perfecto", spanishName: "Pretérito Perfecto Compuesto",
    usageEn: "For past actions with a connection to the present, or that happened in a time period not yet finished (hoy, esta semana).",
    usageDe: "Für vergangene Handlungen mit Bezug zur Gegenwart oder in einem noch nicht abgeschlossenen Zeitraum (hoy, esta semana).",
  },
  {
    mood: Mood.INDICATIVO, tense: Tense.PRETERITO_PLUSCUAMPERFECTO,
    nameEn: "Past Perfect", nameDe: "Plusquamperfekt", spanishName: "Pretérito Pluscuamperfecto",
    usageEn: "For actions that happened before another past action. Equivalent to 'had done' in English.",
    usageDe: "Für Handlungen, die vor einer anderen Vergangenheitshandlung stattfanden. Entspricht dem deutschen Plusquamperfekt.",
  },
  {
    mood: Mood.INDICATIVO, tense: Tense.FUTURO_SIMPLE,
    nameEn: "Simple Future", nameDe: "Futur / Futuro Simple", spanishName: "Futuro Simple",
    usageEn: "For future actions, predictions, and promises. Also expresses probability in the present (¿Dónde estará? = Where could he be?).",
    usageDe: "Für zukünftige Handlungen, Vorhersagen und Versprechen. Drückt auch Wahrscheinlichkeit in der Gegenwart aus.",
  },
  {
    mood: Mood.INDICATIVO, tense: Tense.FUTURO_PERFECTO,
    nameEn: "Future Perfect", nameDe: "Futur II", spanishName: "Futuro Perfecto",
    usageEn: "For actions that will have been completed before a specific future moment. Also expresses probability about past events.",
    usageDe: "Für Handlungen, die vor einem zukünftigen Zeitpunkt abgeschlossen sein werden. Auch für Vermutungen über die Vergangenheit.",
  },
  {
    mood: Mood.INDICATIVO, tense: Tense.CONDICIONAL_SIMPLE,
    nameEn: "Conditional", nameDe: "Konditional / Konjunktiv II", spanishName: "Condicional Simple",
    usageEn: "For hypothetical situations, polite requests, and reported speech about the future. Equivalent to 'would do' in English.",
    usageDe: "Für hypothetische Situationen, höfliche Bitten und indirekte Rede über die Zukunft. Entspricht 'würde + Infinitiv'.",
  },
  {
    mood: Mood.INDICATIVO, tense: Tense.CONDICIONAL_PERFECTO,
    nameEn: "Conditional Perfect", nameDe: "Konditionalperfekt", spanishName: "Condicional Perfecto",
    usageEn: "For hypothetical past actions that did not happen. Equivalent to 'would have done' in English.",
    usageDe: "Für hypothetische vergangene Handlungen, die nicht stattgefunden haben. Entspricht 'hätte + Partizip'.",
  },
  // ── Subjuntivo ───────────────────────────────────────────────────────────────
  {
    mood: Mood.SUBJUNTIVO, tense: Tense.PRESENTE,
    nameEn: "Present Subjunctive", nameDe: "Konjunktiv Präsens", spanishName: "Presente de Subjuntivo",
    usageEn: "Used after expressions of wish, doubt, emotion, or impersonal phrases (quiero que, es importante que). Refers to present or future.",
    usageDe: "Nach Ausdrücken von Wunsch, Zweifel, Emotion oder unpersönlichen Wendungen (quiero que, es importante que). Bezieht sich auf Gegenwart oder Zukunft.",
  },
  {
    mood: Mood.SUBJUNTIVO, tense: Tense.IMPERFECTO_RA,
    nameEn: "Imperfect Subjunctive (-ra)", nameDe: "Konjunktiv Imperfekt (-ra)", spanishName: "Pretérito Imperfecto de Subjuntivo (-ra)",
    usageEn: "The standard form of the past subjunctive. Used in hypothetical sentences (si tuviera...), polite requests, and after past main verbs.",
    usageDe: "Die Standardform des Konjunktiv Imperfekt. Für hypothetische Sätze (si tuviera...), höfliche Bitten und nach Vergangenheitsverben im Hauptsatz.",
  },
  {
    mood: Mood.SUBJUNTIVO, tense: Tense.IMPERFECTO_SE,
    nameEn: "Imperfect Subjunctive (-se)", nameDe: "Konjunktiv Imperfekt (-se)", spanishName: "Pretérito Imperfecto de Subjuntivo (-se)",
    usageEn: "An alternative, more literary form of the -ra subjunctive. Identical in meaning, less common in speech.",
    usageDe: "Eine alternative, literarischere Form des -ra-Konjunktivs. Bedeutungsgleich, in der gesprochenen Sprache seltener.",
  },
  {
    mood: Mood.SUBJUNTIVO, tense: Tense.PRETERITO_PERFECTO_COMPUESTO,
    nameEn: "Present Perfect Subjunctive", nameDe: "Konjunktiv Perfekt", spanishName: "Pretérito Perfecto de Subjuntivo",
    usageEn: "Expresses doubt, wish, or emotion about a completed action. Used after present-tense main verbs (espero que haya llegado).",
    usageDe: "Drückt Zweifel, Wunsch oder Emotion über eine abgeschlossene Handlung aus. Nach Hauptverben im Präsens.",
  },
  {
    mood: Mood.SUBJUNTIVO, tense: Tense.PRETERITO_PLUSCUAMPERFECTO,
    nameEn: "Past Perfect Subjunctive", nameDe: "Konjunktiv Plusquamperfekt", spanishName: "Pretérito Pluscuamperfecto de Subjuntivo",
    usageEn: "For hypothetical situations in the past that did not happen (si hubiera sabido...). Used in the if-clause of past counterfactuals.",
    usageDe: "Für hypothetische vergangene Situationen, die nicht eingetreten sind (si hubiera sabido...). Im Bedingungssatz vergangener Kontrafaktiva.",
  },
  // ── Imperativo ───────────────────────────────────────────────────────────────
  {
    mood: Mood.IMPERATIVO, tense: Tense.IMPERATIVO_AFIRMATIVO,
    nameEn: "Imperative (positive)", nameDe: "Imperativ (bejahend)", spanishName: "Imperativo Afirmativo",
    usageEn: "Direct positive commands. The tú form is unique; all other forms use the present subjunctive.",
    usageDe: "Direkte bejahende Befehle. Die tú-Form ist einzigartig; alle anderen Formen nutzen den Konjunktiv Präsens.",
  },
  {
    mood: Mood.IMPERATIVO, tense: Tense.IMPERATIVO_NEGATIVO,
    nameEn: "Imperative (negative)", nameDe: "Imperativ (verneinend)", spanishName: "Imperativo Negativo",
    usageEn: "Direct negative commands (No hagas eso). All forms use the present subjunctive with no.",
    usageDe: "Direkte verneinende Befehle (No hagas eso). Alle Formen nutzen den Konjunktiv Präsens mit no.",
  },
]

// Lookup helper: TENSE_INFO_MAP[Mood.INDICATIVO][Tense.PRESENTE]
export const TENSE_INFO_MAP: Partial<Record<Mood, Partial<Record<Tense, TenseInfo>>>> =
  TENSE_INFO.reduce((acc, info) => {
    if (!acc[info.mood]) acc[info.mood] = {}
    acc[info.mood]![info.tense] = info
    return acc
  }, {} as Partial<Record<Mood, Partial<Record<Tense, TenseInfo>>>>)
