import Fastify from "fastify"
import { verbRoutes } from "./routes/verbs"

const server = Fastify({ logger: true })

server.get("/health", async () => ({ ok: true }))

server.register(verbRoutes, { prefix: "/verbs" })

const start = async () => {
  try {
    await server.listen({ port: 3001, host: "0.0.0.0" })
  } catch (err) {
    server.log.error(err)
    process.exit(1)
  }
}

start()
