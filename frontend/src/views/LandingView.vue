<script setup lang="ts">
</script>
<template>
  <div class="landing">
    <div class="landing-inner">

      <header class="landing-hero">
        <div class="owl-icon">🦉</div>
        <div class="eyebrow mono">Night Shift Roadmap</div>
        <h1 class="display">Learn at your own pace,<br />on your own schedule.</h1>
        <p class="landing-summary">
          A weekly study planner built for people who work nights. Pick up where
          you left off each day with a rotating curriculum that fits around your
          shift - no deadlines, no pressure.
        </p>
        <div class="landing-cta">
          <router-link to="/login" class="btn btn-amber">Sign in</router-link>
          <router-link to="/register" class="btn btn-outline">Create an account</router-link>
        </div>
      </header>

      <section class="features">
        <div class="feature-card">
          <div class="feature-icon">📅</div>
          <h3 class="display">Weekly curriculum</h3>
          <p>Seven topics rotate through the week - from math and algorithms to
            system design and AI - so you always have something fresh to study.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🌙</div>
          <h3 class="display">Shift-aware schedule</h3>
          <p>Tell the app when you work and it builds a daily timeline around your
            hours, so study time slots actually make sense for your life.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">📈</div>
          <h3 class="display">Track your progress</h3>
          <p>Mark lessons complete as you go. Your progress is saved automatically
            and you can pick up right where you left off.</p>
        </div>
      </section>

      <footer class="landing-footer">
        <div class="credit-footer">
          Created by <strong>Wei Zhu</strong> | Completely for Free
        </div>
        <div class="social-links">
          <a href="https://github.com/ewojjowe" target="_blank" aria-label="GitHub">GitHub</a>
          <a href="www.linkedin.com/in/john-wilfred-montilde" target="_blank" aria-label="LinkedIn">LinkedIn</a>
        </div>
      </footer>

    </div>
  </div>
</template>

<style scoped>
.landing {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
}

.landing-inner {
  max-width: 720px;
  width: 100%;
}

/* ---- Hero ---- */
.landing-hero {
  text-align: center;
  margin-bottom: 56px;
}

.owl-icon {
  font-size: 56px;
  margin-bottom: 16px;
}

.landing-hero .eyebrow {
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--amber);
  margin-bottom: 12px;
}

.landing-hero h1 {
  font-size: clamp(26px, 5vw, 38px);
  font-weight: 700;
  letter-spacing: -0.01em;
  margin: 0 0 16px;
  line-height: 1.2;
}

.landing-summary {
  color: var(--text-muted);
  font-size: 15px;
  max-width: 520px;
  margin: 0 auto 28px;
  line-height: 1.6;
}

.landing-cta {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.landing-cta .btn {
  padding: 12px 28px;
  font-size: 14px;
  text-decoration: none;
  display: inline-block;
}

/* ---- Features ---- */
.features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 56px;
}

@media (max-width: 600px) {
  .features {
    grid-template-columns: 1fr;
  }
}

.feature-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 22px 20px;
}

.feature-icon {
  font-size: 28px;
  margin-bottom: 10px;
}

.feature-card h3 {
  font-size: 15px;
  font-weight: 700;
  margin: 0 0 8px;
}

.feature-card p {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
  line-height: 1.55;
}

/* ---- Footer ---- */
.landing-footer {
  border-top: 1px solid var(--border);
  padding-top: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.social-links {
  display: flex;
  gap: 16px;
}

.social-links a {
  font-size: 12px;
  color: var(--text-muted);
  text-decoration: none;
  font-family: "IBM Plex Mono", monospace;
  letter-spacing: 0.02em;
}

.social-links a:hover {
  color: var(--teal);
}
</style>
