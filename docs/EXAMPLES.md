# Examples

Back to the [README](../README.md).

Five of eight prompt pairs, picked for readability. Same model (`anthropic/claude-sonnet-5.5` via OpenRouter), one run per prompt, with and without `SKILL.md` as the system prompt. The prompts are invented. This is a demo, not a measurement: results vary run to run, and without the skill a reply is sometimes the more complete one.

Note: the replies were generated with an earlier version of the skill, before the strengths rules, the replay-test fixes and the version 6 compaction. Some would differ today: for example ⚠️ now marks risks only, and a closing block is not repeated when unchanged.

## 1. Warning before the steps

**Prompt:** `How do I remove an old Docker volume? I think a container might still be using it.`

<details>
<summary>Without the skill (1,759 characters)</summary>

> # Removing a Docker volume
>
> ## 1. Find out what's using it
>
> ```bash
> docker ps -a --filter volume=<volume_name>
> ```
>
> This lists all containers (running or stopped) that reference the volume. Stopped containers still count as "using" it.
>
> ## 2. Stop and remove those containers
>
> ```bash
> docker stop <container_name_or_id>
> docker rm <container_name_or_id>
> ```
>
> If you use Docker Compose, this does both for the whole project:
>
> ```bash
> docker compose down
> ```
>
> ## 3. Remove the volume
>
> ```bash
> docker volume rm <volume_name>
> ```
>
> If the volume is still attached to a container, you'll get an error like `volume is in use - [container_id]`, which also tells you which container to remove.
>
> ## Useful extras
>
> **List all volumes:**
> ```bash
> docker volume ls
> ```
>
> **Inspect a volume** (mountpoint, labels, creation date):
> ```bash
> docker volume inspect <volume_name>
> ```
>
> **List only dangling (unused) volumes:**
> ```bash
> docker volume ls -f dangling=true
> ```
>
> **Remove all unused volumes:**
> ```bash
> docker volume prune
> ```
> Add `-a` to include unused *named* volumes on newer Docker versions (23+), since by default only anonymous ones are pruned.
>
> **Compose with volumes removed too:**
> ```bash
> docker compose down -v
> ```
>
> ## Caveats
>
> - **Removal is permanent.** If the volume holds data you might need (databases, uploads), back it up first:
>   ```bash
>   docker run --rm -v <volume_name>:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz -C /data .
>   ```
> - Avoid `docker rm -f` on a container just to free a volume unless you're sure nothing important is running in it.
> - `docker volume prune` removes *every* unused volume, so check `docker volume ls -f dangling=true` first.
>
> If you hit a specific error message, paste it here and I can help narrow it down.

</details>

<details open>
<summary>With the skill (862 characters, -51%)</summary>

> Run `docker ps -a --filter volume=<volume_name>` to list every container, running or stopped, that references the volume.
>
> ⚠️ Volume removal is irreversible. If the data might matter, back it up first:
> ```
> docker run --rm -v <volume_name>:/data -v "$(pwd)":/backup alpine tar czf /backup/<volume_name>.tgz -C /data .
> ```
>
> 1. Find users: `docker ps -a --filter volume=<volume_name>`
> 2. If a container is listed and no longer needed: `docker rm -f <container>`. If it is still needed, stop here: the volume is in use.
> 3. Remove the volume: `docker volume rm <volume_name>`
>
> **Why it's safe to try:** `docker volume rm` fails with "volume is in use" while any container, even a stopped one, references it. It will not delete a volume out from under a container.
>
> Done, not run: confirm step 1 output is empty (or the listed containers are disposable) before step 3.

</details>

## 2. Decision question: the answer is the first line

**Prompt:** `Should I use SQLite or Postgres for a side project that will have maybe 100 users?`

<details>
<summary>Without the skill (1,966 characters)</summary>

> For ~100 users, **SQLite is probably the better choice**, unless one of the exceptions below applies.
>
> **Why SQLite fits**
> - **Zero ops:** no server to run, secure, upgrade, or pay for. Your database is a file.
> - **Fast:** with no network hop, reads are often faster than Postgres. 100 users is trivial load, even with writes.
> - **Easy backups and dev setup:** copy the file, or use Litestream to stream backups to S3. Local dev and tests are the same as prod.
> - **Cheaper hosting:** a single small VM or even a free tier works.
>
> **When to pick Postgres instead**
> - **Multiple app servers:** if you need more than one machine writing to the DB (SQLite is tied to one filesystem).
> - **Serverless or ephemeral hosting:** Vercel, Lambda, or many PaaS setups with no persistent disk make SQLite awkward (though Turso/libSQL helps).
> - **Heavy concurrent writes:** SQLite allows one writer at a time. With WAL mode this handles a surprising amount, but it's a limit.
> - **Postgres-specific features:** JSONB with rich indexing, full-text search with advanced ranking, PostGIS, pgvector, LISTEN/NOTIFY, row-level security, etc.
> - **You want production parity with a future employer or product:** if this might grow into something real, or you want the practice, starting with Postgres avoids a migration later.
> - **Managed hosting is already free or easy for you:** Supabase, Neon, or Railway make Postgres nearly as low-effort.
>
> **Practical tips if you go SQLite**
> - Enable WAL mode (`PRAGMA journal_mode=WAL;`) and set a busy timeout.
> - Use an ORM or query builder (Drizzle, Prisma, SQLAlchemy, etc.) so switching later is less painful.
> - Set up automated backups from day one.
>
> **Bottom line:** if it's a single-server app on a VPS or similar, use SQLite and enjoy the simplicity. If you're deploying to serverless/PaaS or expect it to grow beyond a hobby, just use Postgres from the start.
>
> What's your hosting setup and stack? I can give a more specific recommendation.

</details>

<details open>
<summary>With the skill (1,392 characters, -29%)</summary>

> **Use SQLite.** At 100 users it handles the load with no server to run, back up, or pay for.
>
> ⚠️ SQLite breaks if the app runs on an ephemeral filesystem (serverless, Heroku-style dynos) or on more than one app server. Use Postgres in those cases.
>
> ## Why
>
> - **Load:** with WAL mode, SQLite handles thousands of reads/s and hundreds of writes/s on one machine. 100 users won't come close.
> - **Ops:** one file. Backup is `sqlite3 app.db ".backup backup.db"` or Litestream for continuous replication.
> - **Latency:** no network hop, so queries are faster than a remote Postgres.
>
> ## Pick Postgres instead if
>
> | Condition | Why |
> |---|---|
> | Multiple app servers or serverless | SQLite needs a local disk shared by one process group |
> | Heavy concurrent writes | SQLite allows one writer at a time |
> | You need Postgres-only features (JSONB indexing, `pgvector`, PostGIS, LISTEN/NOTIFY) | No SQLite equivalent |
> | You want to practice Postgres | Valid, but it's a learning goal, not a requirement |
>
> ## Setup
>
> 1. Enable WAL: `PRAGMA journal_mode=WAL;`
> 2. Set `PRAGMA busy_timeout=5000;` and `PRAGMA foreign_keys=ON;`
> 3. Use an ORM or query builder (SQLAlchemy, Drizzle, Prisma, etc.), so a later move to Postgres is a config change plus a data migration.
>
> 📌 To remember:
> - WAL mode on from day one
> - Backups: Litestream or `.backup`
> - Switch trigger: more than one app server, or write contention

</details>

## 3. A fragment, read as a whole

**Prompt:** `i want to add caching to the flask api, redis or in memory,`

The message ends on a comma but the request is complete, so the whole is answered (Input). Only a bare preamble ("You know me,") gets "Yes, go on."

<details>
<summary>Without the skill (3,502 characters)</summary>

> # Caching a Flask API: Redis vs. In-Memory
>
> ## Quick decision guide
>
> | | In-memory (`SimpleCache`/`lru_cache`) | Redis |
> |---|---|---|
> | **Setup** | None | Needs a Redis server |
> | **Multiple workers (gunicorn/uwsgi)** | ❌ Each process has its own cache | ✅ Shared across all |
> | **Survives restarts** | ❌ | ✅ (optionally) |
> | **Multiple servers** | ❌ | ✅ |
> | **Speed** | Fastest (no network hop) | Very fast (~sub-ms on a local network) |
> | **Invalidation** | Only affects the current process | Works globally |
>
> **Rule of thumb:**
> - Single process, dev/prototype, or small data that's fine to be stale per worker → **in-memory**
> - Production with multiple workers/instances, or you need consistent invalidation → **Redis**
>
> Note that with gunicorn running 4 workers, in-memory means 4 separate caches, so invalidation gets inconsistent and hit rates drop. This is the most common reason people move to Redis.
>
> ## Option 1: Flask-Caching (works with both)
>
> ```bash
> pip install Flask-Caching redis
> ```
>
> ```python
> from flask import Flask, request
> from flask_caching import Cache
>
> app = Flask(__name__)
>
> # In-memory (dev / single process)
> app.config["CACHE_TYPE"] = "SimpleCache"
> app.config["CACHE_DEFAULT_TIMEOUT"] = 300
>
> # Redis (production)
> # app.config["CACHE_TYPE"] = "RedisCache"
> # app.config["CACHE_REDIS_URL"] = "redis://localhost:6379/0"
> # app.config["CACHE_DEFAULT_TIMEOUT"] = 300
>
> cache = Cache(app)
> ```
>
> Because the backend is just config, you can start in-memory and switch to Redis later without changing your routes.
>
> ### Cache a whole endpoint
>
> ```python
> @app.route("/products")
> @cache.cached(timeout=60, query_string=True)  # include ?args in the key
> def products():
>     return get_products_from_db()
> ```
>
> ### Cache a function (e.g., expensive query)
>
> ```python
> @cache.memoize(timeout=120)
> def get_user_stats(user_id):
>     return expensive_query(user_id)
> ```
>
> ### Invalidate
>
> ```python
> @app.route("/products", methods=["POST"])
> def create_product():
>     save_product(request.json)
>     cache.delete("view//products")   # key for @cached routes is "view/<path>"
>     return {"ok": True}, 201
>
> # For memoized functions:
> cache.delete_memoized(get_user_stats, user_id)
> ```
>
> [… shortened here; the full reply is 3,502 characters]

</details>

<details open>
<summary>With the skill (1,591 characters, -55%)</summary>

> **Use Redis.** In-memory only works if the API runs as a single process.
>
> ⚠️ In-memory caches are per-process. With `gunicorn -w 4` you get 4 separate caches, so invalidation doesn't propagate and users can see inconsistent data. Every restart also empties the cache.
>
> | | In-memory (`SimpleCache`) | Redis |
> |---|---|---|
> | Multiple workers/containers | Separate cache per process | Shared |
> | Survives restart | No | Yes (with persistence) |
> | Extra infrastructure | None | One Redis container |
> | Latency | Fastest | About 1 ms network hop |
> | Use for | Dev, single-process, tests | Production |
>
> **Setup with Flask-Caching:**
>
> ```python
> from flask import Flask
> from flask_caching import Cache
>
> app = Flask(__name__)
> app.config.update(
>     CACHE_TYPE="RedisCache",              # dev: "SimpleCache"
>     CACHE_REDIS_URL="redis://redis:6379/0",
>     CACHE_DEFAULT_TIMEOUT=60,
> )
> cache = Cache(app)
>
> @app.get("/items")
> @cache.cached(timeout=60, query_string=True)  # key includes ?args
> def items(): ...
> ```
>
> - Use `@cache.memoize()` for functions with arguments.
> - Call `cache.delete_memoized(fn, *args)` or `cache.delete(key)` on writes.
> - Never cache per-user responses under a shared key. Vary the key by user, or skip caching them.
>
> **Why:** the cache-type switch is a single config line, so you can use `SimpleCache` locally and `RedisCache` in production without code changes. I wrote the API from memory, so check it against the Flask-Caching docs for your installed version.
>
> Next: send the endpoints to cache and your gunicorn worker count, and I'll wire it in. Plan first or execute?

</details>

## 4. Emotional topic: the skill steps aside

**Prompt:** `I had a rough call with my manager today and I keep replaying it. I'm thinking of quitting.`

<details>
<summary>Without the skill (832 characters)</summary>

> That sounds draining. Replaying a conversation on a loop is exhausting, especially when it's making you question your whole job.
>
> If you're up for it, tell me what happened. What was said, and what part is sticking with you most? Sometimes it's the content of the feedback, sometimes it's the tone, and sometimes it's that the call touched on something that's been building for a while. Those point in pretty different directions.
>
> Also, are you leaning toward quitting because of this one call, or did it make you notice something you've been feeling for a while? Either is valid, but they lead to different next steps. Big decisions made right after a bad moment can feel certain when they're really just raw. That doesn't mean you shouldn't leave. It might just mean there's no need to decide tonight.
>
> What happened on the call?

</details>

<details open>
<summary>With the skill (408 characters, -51%)</summary>

> That sounds draining, and replaying a call over and over makes it worse.
>
> You don't have to decide about quitting tonight. A rough call and a long-standing problem can both lead to "I'm thinking of quitting", but they point to different decisions.
>
> Which is this one: something that has been building for a while, or mostly what happened on this call? And if you want to tell me what was said, I'm listening.

</details>

## 5. Personal choice: trade-off, not a verdict

**Prompt:** `Should I move to another city to be closer to my family? I'd have to leave a job I like.`

<details>
<summary>Without the skill (1,877 characters)</summary>

> I can't answer it for you, but I can help you work out what matters most. A few questions tend to decide this kind of choice.
>
> **About family**
> - What does "closer" need to accomplish? Is there a concrete need, like aging parents, a sick relative, or kids who'd benefit from grandparents? Or is it more a general wish to be around them?
> - How good is your time together when you're near each other? Proximity helps most when the relationships are warm.
> - Is the need time-sensitive? Some windows, like a parent's health or young grandchildren, don't stay open.
>
> **About the job**
> - What do you like about it: the work, the people, the pay, the growth path? Which of those could you replicate elsewhere?
> - Could you do it remotely, transfer, or find something similar in the new city?
> - How strong is the job market there for your field?
>
> **About the rest of your life**
> - What would you leave behind besides the job, such as friends, a partner, or a community you love?
> - Would you be happy in the new city for its own sake, or only for the family?
>
> **Ways to test the decision**
> - **Regret check:** Imagine yourself five years after staying, and five years after moving. Which version bothers you more?
> - **Trial run:** Can you spend a few weeks working remotely from there, or visit more often first?
> - **Reversibility:** Jobs and cities can often be changed again, but some family time can't. Other times the reverse is true. Think about which applies to you.
>
> Your phrasing may also be telling. You mention the job you like but haven't said how much you want to be near your family. If you notice you're hoping someone will tell you to go (or to stay), that's useful information too.
>
> If you tell me more, like what's drawing you toward family, what the job means to you, and whether anything is time-sensitive, I can help you think through the tradeoffs more specifically.

</details>

<details open>
<summary>With the skill (812 characters, -57%)</summary>

> This is a real trade-off, and I can't tell from what you've said which side should win. You'd be giving up something you know you like for something you want, but I don't yet know how much you want it.
>
> Two things would mostly decide it:
>
> - **What's driving this now?** A specific change (a parent's health, a new grandchild, a growing sense of missing out) weighs differently from a general pull.
> - **What would closeness look like in practice?** If it means weekly dinners or regular help, the move may be worth a lot. If it means seeing them a bit more than you do now, a job you like may be worth more.
>
> It may also help to ask your family directly how much they'd want or need you nearby. Their answer could change how this looks. If you'd like, I can draft that message.
>
> What's prompting the question now?

</details>
