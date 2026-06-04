import type { FastifyInstance } from "fastify"
import { PrismaClient } from "@prisma/client"
import type { VerbDetail, VerbSummary } from "@verb-master/shared"

const prisma = new PrismaClient()

export async function verbRoutes(fastify: FastifyInstance) {
  // GET /verbs/random — lightweight verb for quiz card, no conjugations
  fastify.get("/random", async (request, reply) => {
    const count = await prisma.verb.count()
    if (count === 0) return reply.status(404).send({ error: "No verbs in database" })

    const skip = Math.floor(Math.random() * count)
    const verb = await prisma.verb.findFirst({ skip })

    if (!verb) return reply.status(404).send({ error: "Not found" })

    const summary: VerbSummary = {
      id:             verb.id,
      infinitive:     verb.infinitive,
      translationsEn: verb.translationsEn as string[],
      translationsDe: verb.translationsDe as string[],
      gerund:         verb.gerund,
      pastParticiple: verb.pastParticiple,
      isReflexive:    verb.isReflexive,
      cefrLevel:      verb.cefrLevel,
      thematicGroup:  verb.thematicGroup,
      tags:           verb.tags as string[],
    }

    return summary
  })

  // GET /verbs/:id — full verb with all conjugations
  fastify.get<{ Params: { id: string } }>("/:id", async (request, reply) => {
    const verb = await prisma.verb.findUnique({
      where: { id: request.params.id },
      include: { conjugations: { include: { rule: true } } },
    })

    if (!verb) return reply.status(404).send({ error: "Not found" })

    const detail: VerbDetail = {
      id:             verb.id,
      infinitive:     verb.infinitive,
      translationsEn: verb.translationsEn as string[],
      translationsDe: verb.translationsDe as string[],
      gerund:         verb.gerund,
      pastParticiple: verb.pastParticiple,
      isReflexive:    verb.isReflexive,
      cefrLevel:      verb.cefrLevel,
      thematicGroup:  verb.thematicGroup,
      tags:           verb.tags as string[],
      conjugations:   verb.conjugations.map((c) => ({
        mood:        c.mood,
        tense:       c.tense,
        person:      c.person,
        form:        c.form,
        isIrregular: c.isIrregular,
        ruleCode:    c.rule?.code ?? null,
        noteEn:      c.noteEn,
        noteDe:      c.noteDe,
      })),
    }

    return detail
  })

  // GET /verbs/:id/conjugations — conjugations only
  fastify.get<{ Params: { id: string } }>("/:id/conjugations", async (request, reply) => {
    const conjugations = await prisma.conjugation.findMany({
      where: { verbId: request.params.id },
      include: { rule: true },
    })

    if (conjugations.length === 0) return reply.status(404).send({ error: "Not found" })

    return conjugations.map((c) => ({
      mood:        c.mood,
      tense:       c.tense,
      person:      c.person,
      form:        c.form,
      isIrregular: c.isIrregular,
      ruleCode:    c.rule?.code ?? null,
      noteEn:      c.noteEn,
      noteDe:      c.noteDe,
    }))
  })
}
