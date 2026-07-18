document.documentElement.classList.add("js");

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function setupReveal() {
  const items = [...document.querySelectorAll(".reveal")];
  if (reducedMotion || !("IntersectionObserver" in window)) {
    items.forEach((item) => item.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-visible");
      observer.unobserve(entry.target);
    });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });

  items.forEach((item) => observer.observe(item));
}

function setupProgressAndNavigation() {
  const progress = document.querySelector("[data-progress]");
  const navLinks = [...document.querySelectorAll(".site-nav a")];
  const sections = [...document.querySelectorAll("[data-section]")];

  const updateProgress = () => {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const ratio = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
    if (progress) progress.style.width = `${ratio * 100}%`;
  };

  updateProgress();
  window.addEventListener("scroll", updateProgress, { passive: true });

  if (!("IntersectionObserver" in window)) return;
  const observer = new IntersectionObserver((entries) => {
    const visible = entries
      .filter((entry) => entry.isIntersecting)
      .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (!visible) return;
    const sectionName = visible.target.dataset.section;
    navLinks.forEach((link) => {
      const target = link.getAttribute("href").slice(1);
      link.classList.toggle("is-active", target === sectionName);
    });
  }, { rootMargin: "-22% 0px -62% 0px", threshold: [0, 0.1, 0.35] });

  sections.forEach((section) => observer.observe(section));
}

function setupSystemMap() {
  const map = document.querySelector("[data-system-map]");
  if (!map) return;

  const nodes = [...map.querySelectorAll("[data-flow-node]")];
  const paths = [...map.querySelectorAll("[data-flow-path]")];
  const branches = [...map.querySelectorAll("[data-flow-branch]")];
  const routePaths = {
    core: ["core"],
    announcement: ["core", "announcement"],
    news: ["core", "news"],
    policy: ["announcement", "news", "policy"],
    schedule: ["schedule", "core", "news"],
  };

  const selectNode = (node) => {
    const route = node.dataset.flowRoute;
    const activePaths = routePaths[route] || [];

    nodes.forEach((item) => {
      const itemRoute = item.dataset.flowRoute;
      item.classList.toggle("is-route-active", item === node || activePaths.includes(itemRoute));
    });
    paths.forEach((path) => {
      path.classList.toggle("is-route-active", activePaths.includes(path.dataset.flowPath));
    });
    branches.forEach((branch) => branch.classList.toggle("is-route-active", activePaths.includes(branch.dataset.flowBranch)));

    map.dataset.activeRoute = route;
    if (!reducedMotion) {
      map.classList.remove("is-animating");
      void map.offsetWidth;
      map.classList.add("is-animating");
      window.setTimeout(() => map.classList.remove("is-animating"), 900);
    }
  };

  nodes.forEach((node) => node.addEventListener("click", () => selectNode(node)));
}

const githubBase = "https://github.com/lunatik-210/gconf/blob/main/";

const link = (url, label, meta = "") => `<a class="dialog-link" href="${url}" target="_blank" rel="noopener noreferrer"><b>${label}</b>${meta ? `<span>${meta}</span>` : ""}</a>`;
const evidence = (status, claim, source, limitation = "") => {
  const label = status === "unindexed" ? "unindexed observation" : status;
  return `<article class="dialog-evidence"><span class="dialog-status dialog-status--${status}">${label}</span><p>${claim}</p><small>${source}</small>${limitation ? `<em>${limitation}</em>` : ""}</article>`;
};
const agentDetails = (input, output, cannot, gate) => `<dl class="dialog-ledger"><dt>input</dt><dd>${input}</dd><dt>output</dt><dd>${output}</dd><dt>не может</dt><dd>${cannot}</dd><dt>решает человек</dt><dd>${gate}</dd></dl>`;

const modalData = {
  "source-telegram": {
    kicker: "SOURCE · TELEGRAM",
    title: "Публичные Telegram-каналы",
    summary: "Telegram выгрузил вручную: прямое подключение в рамках тестового оказалось неоправданно сложным.",
    body: `<div class="dialog-links">${link("https://t.me/gptlovers", "GCONF / AI LOVERS", "история запусков и свежий публичный срез")}${link("https://t.me/Matskevich", "ии и новый мир · Дима Мацкевич", "авторская рамка AI-сдвигов")}${link("https://t.me/aigency_ru", "[айдженси] ИИ в бизнесе", "прикладные business-сигналы")}</div><p class="dialog-note">Закрытые Telegram-группы и restricted locators в публичную презентацию не выносил.</p>`,
  },
  "source-instagram": {
    kicker: "SOURCE · INSTAGRAM",
    title: "Два аккаунта, 22 поста",
    summary: "Публичные посты и доступные комментарии собрал в одноразовом agent-assisted проходе.",
    body: `<div class="dialog-links">${link("https://www.instagram.com/gconf.io/", "@gconf.io", "7 последних постов · карусели · comments snapshot")}${link("https://www.instagram.com/matskevich/", "@matskevich", "15 последних постов · формулировки · reactions snapshot")}</div>${evidence("inference", "Использовал комментарии как evidence языка, вопросов и pains, а не как доказательство продуктовых возможностей.", "Instagram public comments · snapshot 13.07.2026")}${evidence("limitation", "Сохранил лайки и количество комментариев как snapshot, но не включал их в scoring стратегии или тем.", "Local Instagram exports")}`,
  },
  "source-youtube": {
    kicker: "SOURCE · YOUTUBE",
    title: "5 каналов · 10 research packages",
    summary: "Каждый пакет сохраняет title, URL, metadata, time-bound statistics, comments и transcript/captions с provenance.",
    body: `<div class="youtube-groups">
      <section><h3>Dima Matskevich · 2</h3>${link("https://www.youtube.com/watch?v=6WEsPzHyD9k", "Как пользоваться AI в 2026, если вы не технарь?")}${link("https://www.youtube.com/watch?v=XScJOCjDx1M", "AI, AGI, вайб-кодинг и масштаб работы")}</section>
      <section><h3>matskevich ai · 2</h3>${link("https://www.youtube.com/watch?v=gQ4LhTYadK4", "AI-first workflow: найм, контекст и вайбкодинг")}${link("https://www.youtube.com/watch?v=J9cvaJ5enIw", "Cursor, Codex, Claude Code — что важно в 2026")}</section>
      <section><h3>Matt Wolfe · 4</h3>${link("https://www.youtube.com/watch?v=NVP_paJarG4", "AI News: Fable's Back But This New Model is Better?")}${link("https://www.youtube.com/watch?v=yke4fLQUsh4", "Build An AI Second Brain Knowledge Base")}${link("https://www.youtube.com/watch?v=EOCRtSnvNNE", "AI News: GPT-5.6 and the new Super App")}${link("https://www.youtube.com/watch?v=MDy_b9F7oUc", "Complete Guide to ChatGPT 5.6")}</section>
      <section><h3>Wes Roth · 1</h3>${link("https://www.youtube.com/watch?v=cwf2vEAigKA", "Claude Built the Ultimate Second Brain")}</section>
      <section><h3>Илья Рыбалко · 1</h3>${link("https://www.youtube.com/watch?v=TsBK35YnwBs", "Дима Мацкевич про эволюцию человека и AI")}</section>
    </div>`,
  },
  "source-history": {
    kicker: "SOURCE · GCONF",
    title: "Живой offer и история запусков",
    summary: "gconf.io задаёт baseline текущего продукта; Telegram показывает, как менялось доступное поведение.",
    body: `<div class="dialog-links">${link("https://www.gconf.io/", "gconf.io", "current-offer baseline · accessed 17.07.2026")}${link("https://t.me/gptlovers/192", "GCONF 1 · 2023", "живая практика вместо пассивной конференции")}${link("https://t.me/gptlovers/791", "Мета-навыки · 2025", "системное взаимодействие и персональная система")}${link("https://t.me/gptlovers/910", "Vibe Coding · март 2026", "кодинг-агенты")}${link("https://t.me/gptlovers/977", "AI & Vibe Coding · май 2026", "универсальный паттерн работы с агентами")}${link("https://t.me/gptlovers/1009", "AI weekend · июль 2026", "первый agentic workflow")}${link("https://t.me/gptlovers/1040", "Vibe Coding · июль 2026", "личная система агентов")}</div>`,
  },
  "source-labs": {
    kicker: "SOURCE · OFFICIAL LABS",
    title: "Первичные release и research pages",
    summary: "Собрал web-материалы в локальные snapshots с помощью агентов; перед writer-run повторно открыл первичные страницы.",
    body: `<div class="dialog-links">${link("https://deepmind.google/blog/securing-the-future-of-ai-agents/", "Google DeepMind", "agent security and control")}${link("https://www.anthropic.com/research/claude-code-expertise", "Anthropic", "domain expertise and agent execution")}${link("https://www.kimi.com/blog/kimi-k3", "Kimi / Moonshot AI", "Kimi K3 release")}${link("https://openai.com/index/separating-signal-from-noise-coding-evaluations/", "OpenAI", "coding evaluation methodology")}${link("https://z.ai/blog/glm-5-2", "Z.ai", "frontier-model signal")}</div><p class="dialog-note">Publisher benchmarks остаются publisher claims и получают risk penalty.</p>`,
  },
  "collection-youtube": {
    kicker: "AGENT STEP · gconf-youtube-research",
    title: "gconf-youtube-research",
    summary: "Агент выполняет сбор по repository skill: тот задаёт контракт артефакта, helpers и границы шага.",
    body: `${agentDetails("YouTube URL или существующий video snapshot", "metadata, statistics, comments, chapters, description, thumbnail, captions или transcript", "писать в SQLite/Obsidian, архивировать видео или подменять отсутствующие данные", "принять completeness snapshot и передать готовый package в Ingest")}<p class="dialog-note"><code>yt-dlp</code> используется для probe/captions, локальный Whisper — только fallback, когда captions недоступны.</p>`,
  },
  "collection-local": {
    kicker: "COLLECTION · LOCAL PACKAGES",
    title: "Честная граница collection",
    summary: "Telegram собрал вручную; Instagram и web — в одноразовых агентных проходах.",
    body: `${evidence("fact", "В репозитории нет reusable Telegram-, Instagram- или general web crawler skill.", "AGENTS.md · collection boundaries")}${evidence("fact", "Ingest принимает только уже существующие локальные packages и никогда не скачивает источники.", "gconf-knowledge-ingest contract")}<div class="dialog-upgrade"><span>potential upgrade</span><p>MCP/connectors или scheduled collection могут убрать ручной intake, но не должны обходить human gates.</p></div>`,
  },
  "collection-schedule": {
    kicker: "PROPOSAL · NOT DEPLOYED",
    title: "Сбор можно поставить на cadence",
    summary: "Schedule может запускать доступный collection и News Radar, но сейчас в проекте не развёрнут.",
    body: `${agentDetails("временной trigger + разрешённый source scope", "новый source snapshot или radar-run", "самостоятельно утверждать evidence, выбирать тему, писать или публиковать", "частота, стоимость, доступы и реакция на ошибки")}`,
  },
  "agent-ingest": {
    kicker: "AGENT STEP · gconf-knowledge-ingest",
    title: "Собирает проверяемый индекс",
    summary: "Агент по skill-контракту детерминированно импортирует уже собранные артефакты без semantic judgment.",
    body: agentDetails("готовые YouTube, Telegram, Instagram, Web Article и local research packages", "SQLite/FTS, relations, checksums, source cards и ingestion report", "собирать источники, транскрибировать или делать редакционные выводы", "scope источников и запуск ingestion"),
  },
  database: {
    kicker: "KNOWLEDGE · MACHINE INDEX",
    title: "SQLite / FTS",
    summary: "Пересобираемый индекс для точного поиска, provenance и связей между 7 942 документами.",
    body: `${evidence("fact", "Индекс содержит normalized documents, comments, 2 405 transcript chunks, reply edges, checksums и full-text search.", "knowledge/_index/gconf.sqlite · snapshot 17.07.2026")}${evidence("limitation", "SQLite — производный машинный слой, а не editorial source of truth.", "AGENTS.md · knowledge flow")}`,
  },
  "agent-extract": {
    kicker: "AGENT STEP · gconf-insight-extract",
    title: "Вынимает semantic candidates",
    summary: "Агент читает полный evidence batch и по skill-контракту создаёт traceable Obsidian-карточки.",
    body: agentDetails("одна pending/stale evidence batch из SQLite", "typed pains, cases, trends, technologies, actors, cohorts и claims со статусом candidate", "выходить в сеть, писать публичный текст или повышать candidate до approved", "semantic review каждой кандидатной карточки"),
  },
  obsidian: {
    kicker: "KNOWLEDGE · OBSIDIAN",
    title: "Карточки, которые можно проверить",
    summary: "Каждая candidate-card хранит status, exact locators, короткие quotes, dates, relationships и limitations.",
    body: `${evidence("fact", "Папка не определяет approval: для этого существует review_status.", "knowledge/ · Obsidian vault")}${evidence("limitation", "Завершённый processing fingerprint означает, что batch обработан, а не что смысл одобрен человеком.", "knowledge/processing/")}`,
  },
  "reviewed-knowledge": {
    kicker: "HUMAN GATE · REVIEWED KNOWLEDGE",
    title: "Одобренный semantic layer",
    summary: "Только после человеческой проверки candidate может войти в editorial retrieval как reviewed knowledge.",
    body: agentDetails("candidate-card + rendered evidence", "approved или отклонённое редакционное решение", "автоматически наследовать доверие из score, validator или processing marker", "значение, достаточность evidence и допустимое использование"),
  },
  "agent-analysis": {
    kicker: "AGENT STEP · gconf-announcement-analysis",
    title: "Предлагает направления анонса",
    summary: "Агент сопоставляет live offer, историю, аудиторию, protagonists и свежие AI-сигналы.",
    body: agentDetails("reviewed knowledge + live gconf.io + history + Tone of Voice", "2–3 ranked directions с evidence refs, risks и channel jobs", "выбирать стратегию или писать публичный анонс", "одно направление и его поведенческий переход"),
  },
  "agent-announcement-writer": {
    kicker: "AGENT STEP · gconf-announcement-writer",
    title: "Пишет Telegram, слайды и caption",
    summary: "Агент работает только по выбранному direction ID и подтверждённому allowlist фактов.",
    body: agentDetails("selected direction + confirmed facts + prior locators + GCONF ToV", "Telegram draft + ровно 6 Instagram slides + caption + evidence ledger", "изобретать даты, цену, программу, разрешения или менять стратегию", "copy, commercial facts, attribution и permissions"),
  },
  "agent-carousel": {
    kicker: "AGENT STEP · gconf-instagram-carousel-designer",
    title: "Собирает шесть визуальных слайдов",
    summary: "Агент переводит approved copy в единый 1080×1350 visual run по дизайнерскому skill-контракту.",
    body: agentDetails("утверждённый six-slide copy + локальные visual references", "6 validated WebP images и audit artifacts", "удалять смысл ради layout, добавлять claims или публиковать", "visual approval каждой финальной картинки"),
  },
  "agent-radar": {
    kicker: "AGENT STEP · gconf-news-radar",
    title: "Собирает newsroom shortlist",
    summary: "Агент обходит source lanes, объединяет сигналы, проверяет prior coverage, дедуплицирует и считает priority score.",
    body: agentDetails("live public signals + full local knowledge + prior GCONF coverage", "validated backlog с recommended, reserve и reject", "выбирать topic ID, писать пост или повышать score ради квоты", "один или несколько topic ID") ,
  },
  "agent-news-writer": {
    kicker: "AGENT STEP · gconf-news-writer",
    title: "Повторно проверяет источник и пишет",
    summary: "Агент перед текстом заново открывает primary source выбранной человеком темы.",
    body: agentDetails("validated radar-run + explicit topic ID + GCONF ToV", "reviewable Telegram post с фактами, inference и limitations", "подменять stale тему другой или менять radar ranking", "freshness, ограничения и финальный copy") ,
  },
  "agent-formatter": {
    kicker: "AGENT STEP · gconf-telegram-formatter",
    title: "Готовит чистый handoff",
    summary: "Агент форматирует только явно выбранный draft, сохраняя факты, ссылки, CTA и ограничения.",
    body: agentDetails("explicit clean public-copy path", "validated Markdown для ручной публикации", "переписывать, выбирать latest, планировать или публиковать", "точный файл и момент ручной публикации"),
  },
  "tone-of-voice": {
    kicker: "EDITORIAL POLICY · VERSION 1.0",
    title: "Tone of Voice GCONF",
    summary: "Канонический, versioned и human-owned стандарт для обоих Writer и обязательного voice audit.",
    body: `${evidence("fact", "Голос строится вокруг среды, агентности, процесса, мета-навыков и изменения поведения.", "editorial/gconf-tone-of-voice.md · 17.07.2026")}${evidence("limitation", "ToV не разрешает придумывать offer facts и не заменяет evidence review.", "canonical voice standard")}${link(`${githubBase}editorial/gconf-tone-of-voice.md`, "Открыть стандарт в GitHub")}`,
  },
  "publication-upgrade": {
    kicker: "POTENTIAL UPGRADE · NOT DEPLOYED",
    title: "Публикацию можно подключить через MCP",
    summary: "Сейчас handoff публикуется вручную. Следующий шаг — после явного human approval передавать точный утверждённый артефакт в авторизованный MCP-коннектор или scheduled task.",
    body: agentDetails("approved exact artifact + канал + время публикации + разрешённый connector", "немедленная публикация или запланированная задача с audit trail", "публиковать до approval, менять текст, самостоятельно выбирать draft или хранить credentials в репозитории", "точный copy, канал, время, доступы и отмену задачи"),
  },
  "strategy-history": {
    kicker: "AI OPS EVIDENCE · 01",
    title: "История расширяет единицу поведения",
    summary: "Это не один launch claim, а редакционная интерпретация нескольких публичных запусков.",
    body: `<div class="timeline-evidence">${evidence("fact", "2023–2024: живая практика с GPT → ежедневное использование → отраслевые процессы.", "Telegram: gptlovers/192 и исторический корпус")}${evidence("inference", "2025: инструмент → напарник → мета-навыки и собственные проекты.", "Telegram: gptlovers/791")}${evidence("fact", "2026: coding agents → универсальный agent pattern → первый workflow → личная система.", "Telegram: gptlovers/910, /977, /1009, /1040")}</div><div class="dialog-links">${link("https://t.me/gptlovers/192", "GCONF 1")}${link("https://t.me/gptlovers/791", "Мета-навыки")}${link("https://t.me/gptlovers/910", "Vibe Coding · март")}${link("https://t.me/gptlovers/977", "AI & Vibe Coding · май")}${link("https://t.me/gptlovers/1009", "AI weekend")}${link("https://t.me/gptlovers/1040", "Vibe Coding · июль")}${link(`${githubBase}research/gconf_history/GCONF_history_report.md`, "Открыть history report в GitHub")}</div>`,
  },
  "strategy-product": {
    kicker: "AI OPS EVIDENCE · 02",
    title: "Текущий продукт уже заканчивается первым workflow",
    summary: "Structured extraction из live gconf.io, accessed 17.07.2026. Это baseline текущего потока, не факт о следующем.",
    body: `${evidence("unindexed", "Переход: разовые диалоги и технический барьер → личная система агентов, рабочий артефакт, правила и практика.", "gconf.io · live baseline")}${evidence("unindexed", "Обещанные outputs: AI-память, рабочий артефакт, повторяемые правила, ритм и спокойствие вместо FOMO.", "gconf.io · current offer")}${evidence("limitation", "Дата, 21 день и $650 относятся только к текущему cohort 14 и не переносятся в следующий запуск.", "announcement analysis manifest")}${link("https://www.gconf.io/", "Открыть текущий продукт")}`,
  },
  "strategy-audience": {
    kicker: "AI OPS EVIDENCE · 03",
    title: "Аудитория говорит о контроле и сложности перехода",
    summary: "Публичные комментарии подтверждают язык боли, но не capability продукта.",
    body: `${evidence("inference", "“Isn’t that personal data leaving your computer and going somewhere else where you don’t have control over it?”", "@samuraiintellectual · YouTube comment · 16.07.2026", "Вопрос о контроле данных, не доказательство утечки.")}${link("https://www.youtube.com/watch?v=MDy_b9F7oUc&lc=UgwdZbF0D8ns4-hVyk94AaABAg", "Открыть комментарий")}${evidence("inference", "“Bro, you make it sound so easy.”", "@kirkwoodpaterson9510 · YouTube comment · 15.07.2026", "Сигнал demo-to-practice gap.")}${link("https://www.youtube.com/watch?v=cwf2vEAigKA&lc=UgwANiCWq9lmHTlDZRR4AaABAg", "Открыть комментарий")}${evidence("fact", "“создала crm систему для психологов за 7 дней! Я ничего не понимаю в этом, только знала архитектуру, понимала путь клиента и все.”", "@olga_emir · YouTube self-report · 15.06.2026", "Функциональность и срок независимо не проверены.")}${link("https://www.youtube.com/watch?v=6WEsPzHyD9k&lc=UgyRj7j7WWrniJexbJ54AaABAg", "Открыть публичный кейс")}`,
  },
  "strategy-signals": {
    kicker: "AI OPS EVIDENCE · 04",
    title: "Внешние сигналы сходятся к длительной системе",
    summary: "Каждый источник подтверждает свой наблюдаемый сдвиг; общий вывод Living AI Ops остаётся inference.",
    body: `${evidence("inference", "“Agentic AI changes the unit of knowledge work from single interactions to delegated, long-horizon tasks.”", "OpenAI · 25.06.2026")}${link("https://openai.com/index/how-agents-are-transforming-work/", "OpenAI")}${evidence("inference", "“people make most of the planning decisions (what to do) and Claude makes most of the execution decisions (how to do it)”", "Anthropic · 16.06.2026")}${link("https://www.anthropic.com/research/claude-code-expertise", "Anthropic")}${evidence("fact", "«мы полностью перевезли свои процессы на свои вайбкодинг штуки и постоянно их улучшаем»", "GCONF / AI LOVERS · 13.07.2026")}${link("https://t.me/gptlovers/1058", "Дима Мацкевич / GCONF")}${evidence("fact", "“OpenAI just combined ChatGPT, Codex, their browser, and ChatGPT Work into one platform.”", "Matt Wolfe · 15.07.2026")}${link("https://www.youtube.com/watch?v=MDy_b9F7oUc", "Matt Wolfe")}${evidence("fact", "“The guide to building a &quot;second brain&quot; (give it to your chatbot)”", "Wes Roth · 14.07.2026")}${link("https://www.youtube.com/watch?v=cwf2vEAigKA", "Wes Roth")}`,
  },
  "strategy-choice": {
    kicker: "HUMAN GATE · DIRECTION",
    title: "Из трёх направлений выбрал Living AI Ops",
    summary: "Analysis ранжировал варианты, а финальный selection зафиксировал отдельной decision-card.",
    body: `<div class="direction-list"><article class="is-chosen"><span>01 · HIGH · SELECTED</span><h3>Living AI Ops</h3><p>первый workflow → система, которая помнит, выполняет, проверяется и улучшается</p><small>Риск: может прозвучать как ещё больше setup.</small></article><article><span>02 · MEDIUM</span><h3>Агентность с границами</h3><p>«боюсь дать доступ / даю всё» → полномочия растут вместе с контролем</p><small>Риск: страх может подавить любопытство.</small></article><article><span>03 · MEDIUM</span><h3>Предметный эксперт как создатель</h3><p>жду разработчиков → собираю систему вокруг собственного domain knowledge</p><small>Риск: повторить старое no-code обещание.</small></article></div>${evidence("proposal", "AI Ops — редакционная рамка work sample, а не подтверждённая программа следующего потока.", "direction-living-ai-ops")}${link(`${githubBase}research/announcement_analysis/runs/20260717T200356Z/analysis.md`, "Открыть analysis-run")}${link(`${githubBase}knowledge/editorial/decisions/decision-backfill-20260718T100953Z-announcement-direction-selection.md`, "Открыть human decision-card")}`,
  },
};

function scoreBody(scores, rationale, note = "") {
  const total = scores.market + scores.gconf + scores.novelty + scores.evidence + scores.fresh + scores.action - scores.risk;
  return `<div class="score-breakdown"><div><b>${scores.market}</b><span>рынок</span></div><div><b>${scores.gconf}</b><span>GCONF</span></div><div><b>${scores.novelty}</b><span>новизна</span></div><div><b>${scores.evidence}</b><span>evidence</span></div><div><b>${scores.fresh}</b><span>freshness</span></div><div><b>${scores.action}</b><span>action</span></div><div class="is-penalty"><b>−${scores.risk}</b><span>risk</span></div><div class="is-total"><b>${total}</b><span>priority</span></div></div><code class="score-equation">${scores.market} + ${scores.gconf} + ${scores.novelty} + ${scores.evidence} + ${scores.fresh} + ${scores.action} − ${scores.risk} = ${total}</code><p class="score-rationale">${rationale}</p>${note ? `<p class="dialog-note">${note}</p>` : ""}`;
}

Object.assign(modalData, {
  "radar-science": { kicker: "RADAR · RECOMMENDED · HUMAN SELECTED", title: "Science validation · 95", summary: "Два независимых свежих сигнала, новый coverage delta и применимый аудит workflow.", body: scoreBody({market:19,gconf:20,novelty:20,evidence:20,fresh:9,action:9,risk:2}, "Самая сильная связка с новым GCONF: provenance, reviewer layer и воспроизводимость.", "Выбрал тему отдельно; высокий score сам по себе не запускает Writer.") },
  "radar-benchmark": { kicker: "RADAR · RECOMMENDED", title: "Benchmark audit · 89", summary: "Практичная новая методология выбора моделей, но только один корпоративный primary source.", body: scoreBody({market:18,gconf:19,novelty:19,evidence:19,fresh:10,action:8,risk:4}, "Сильный новый угол относительно model-release постов.", "Score выше Kimi, но для второго поста выбрал другую тему.") },
  "radar-kimi": { kicker: "RADAR · RECOMMENDED · HUMAN SELECTED", title: "Kimi K3 · 86", summary: "Самый свежий непокрытый релиз с понятным тестом routing и open caveat.", body: scoreBody({market:19,gconf:17,novelty:20,evidence:18,fresh:10,action:9,risk:7}, "Штраф за publisher-only benchmarks, разные harness и ещё не выпущенные на snapshot веса.", "Выбрал как второй, контрастный editorial angle.") },
  "radar-muse-image": { kicker: "RADAR · RECOMMENDED", title: "Muse Image · 85", summary: "Визуально понятный и новый для канала tool-using workflow.", body: scoreBody({market:16,gconf:17,novelty:20,evidence:18,fresh:10,action:9,risk:5}, "Новый agentic visual process; ограничения — rollout и corporate evals.") },
  "radar-muse-spark": { kicker: "RADAR · RECOMMENDED", title: "Muse Spark · 84", summary: "Сильная связь с AI Ops через model-native orchestration.", body: scoreBody({market:18,gconf:20,novelty:16,evidence:18,fresh:10,action:8,risk:6}, "Тема техническая; большая часть практических claims принадлежит издателю модели.") },
  "radar-copilot": { kicker: "RADAR · RESERVE", title: "Copilot control plane · 77", summary: "Практичный AI Ops пример, но с узкой dev-аудиторией и частичным overlap.", body: scoreBody({market:15,gconf:18,novelty:13,evidence:18,fresh:10,action:9,risk:6}, "Оставил в reserve: cost observability полезна, но угол уже частично покрыт.") },
  "radar-chatgpt-work": { kicker: "RADAR · REJECT · INELIGIBLE DUPLICATE", title: "ChatGPT Work · 79", summary: "Сумма достаточна для reserve, но тема не проходит semantic coverage gate.", body: scoreBody({market:20,gconf:20,novelty:1,evidence:20,fresh:10,action:8,risk:0}, "Entity, центральный claim и переход chat → AI-операционка уже присутствовали в GCONF.", "Eligibility важнее score: без нового evidence-backed delta тему отклонил.") },
  "radar-reflection": { kicker: "RADAR · REJECT", title: "Claude Reflection · 63", summary: "Свежий релиз, но почти тот же GCONF-угол уже был использован.", body: scoreBody({market:15,gconf:15,novelty:2,evidence:18,fresh:10,action:6,risk:3}, "Отклонил: тема ниже порога из-за почти полного совпадения с материалом о Claude Code /insights.") },
});

function setupEvidenceDialog() {
  const dialog = document.querySelector("[data-evidence-dialog]");
  if (!dialog) return;

  const fields = {
    kicker: dialog.querySelector("[data-dialog-kicker]"),
    title: dialog.querySelector("[data-dialog-title]"),
    summary: dialog.querySelector("[data-dialog-summary]"),
    body: dialog.querySelector("[data-dialog-body]"),
  };
  const closeButton = dialog.querySelector("[data-dialog-close]");
  let opener = null;

  const open = (trigger) => {
    const item = modalData[trigger.dataset.dialog];
    if (!item) return;
    opener = trigger;
    fields.kicker.textContent = item.kicker;
    fields.title.textContent = item.title;
    fields.summary.textContent = item.summary;
    fields.body.innerHTML = item.body;
    if (typeof dialog.showModal === "function") dialog.showModal();
    else dialog.setAttribute("open", "");
    closeButton.focus();
  };

  document.querySelectorAll("[data-dialog]").forEach((trigger) => trigger.addEventListener("click", () => open(trigger)));
  closeButton.addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
  dialog.addEventListener("close", () => {
    if (opener) opener.focus();
  });
}

function setupCarousel() {
  const carousel = document.querySelector("[data-carousel]");
  if (!carousel) return;

  const track = carousel.querySelector("[data-carousel-track]");
  const slides = [...track.children];
  const prev = carousel.querySelector("[data-carousel-prev]");
  const next = carousel.querySelector("[data-carousel-next]");
  const dots = carousel.querySelector("[data-carousel-dots]");
  const current = carousel.querySelector("[data-carousel-current]");
  let index = 0;
  let pointerStart = null;

  const dotButtons = slides.map((_, slideIndex) => {
    const button = document.createElement("button");
    button.type = "button";
    button.setAttribute("aria-label", `Показать слайд ${slideIndex + 1}`);
    button.addEventListener("click", () => goTo(slideIndex));
    dots.appendChild(button);
    return button;
  });

  function goTo(nextIndex) {
    index = (nextIndex + slides.length) % slides.length;
    track.style.transform = `translateX(-${index * 100}%)`;
    current.textContent = String(index + 1);
    dotButtons.forEach((dot, dotIndex) => {
      const active = dotIndex === index;
      dot.classList.toggle("is-active", active);
      dot.setAttribute("aria-current", active ? "true" : "false");
    });
  }

  prev.addEventListener("click", () => goTo(index - 1));
  next.addEventListener("click", () => goTo(index + 1));

  carousel.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      goTo(index - 1);
    }
    if (event.key === "ArrowRight") {
      event.preventDefault();
      goTo(index + 1);
    }
  });

  track.addEventListener("pointerdown", (event) => {
    pointerStart = event.clientX;
  });
  track.addEventListener("pointerup", (event) => {
    if (pointerStart === null) return;
    const delta = event.clientX - pointerStart;
    pointerStart = null;
    if (Math.abs(delta) < 45) return;
    goTo(index + (delta < 0 ? 1 : -1));
  });
  track.addEventListener("pointercancel", () => { pointerStart = null; });

  goTo(0);
}

setupReveal();
setupProgressAndNavigation();
setupSystemMap();
setupEvidenceDialog();
setupCarousel();
