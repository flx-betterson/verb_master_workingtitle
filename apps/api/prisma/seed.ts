import { PrismaClient } from "@prisma/client"
import fs from "node:fs"
import path from "node:path"

const prisma = new PrismaClient()

const DATA_PATH = path.join(__dirname, "../../../data/processed/verbs_final.json")

async function main() {
  const raw = fs.readFileSync(DATA_PATH, "utf-8")
  const verbs: any[] = JSON.parse(raw)

  console.log(`Seeding ${verbs.length} verbs...`)

  await prisma.conjugation.deleteMany()
  await prisma.verb.deleteMany()

  let verbCount = 0
  let conjugationCount = 0

  for (const v of verbs) {
    const verb = await prisma.verb.create({
      data: {
        infinitive:     v.infinitive,
        translationsEn: v.translationsEn ?? [],
        translationsDe: v.translationsDe ?? [],
        gerund:         v.gerund ?? "",
        pastParticiple: v.pastParticiple ?? "",
        isReflexive:    v.isReflexive ?? false,
        cefrLevel:      v.cefrLevel ?? "A2",
        thematicGroup:  v.thematicGroup ?? "other",
        tags:           v.tags ?? [],
      },
    })

    const conjugations = (v.conjugations ?? []).map((c: any) => ({
      verbId:      verb.id,
      mood:        c.mood,
      tense:       c.tense,
      person:      c.person,
      form:        c.form,
      isIrregular: c.isIrregular ?? false,
      noteEn:      c.noteEn ?? null,
      noteDe:      c.noteDe ?? null,
    }))

    await prisma.conjugation.createMany({ data: conjugations })

    verbCount++
    conjugationCount += conjugations.length

    if (verbCount % 50 === 0) {
      console.log(`  ${verbCount}/${verbs.length} verbs seeded...`)
    }
  }

  console.log(`Done. ${verbCount} verbs, ${conjugationCount} conjugations seeded.`)
}

main()
  .catch((e) => { console.error(e); process.exit(1) })
  .finally(() => prisma.$disconnect())
