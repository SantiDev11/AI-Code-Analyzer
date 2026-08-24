import React from 'react';
import type { Activity, DailyActivity } from '../types';

interface RepositoryActivityAnalysisProps {
  activity: Activity | null | undefined;
}

interface DailyActivityItemProps {
  day: DailyActivity;
  maxEvents: number;
}

function formatActivityDate(dateStr: string): string {
  try {
    const parsed = new Date(dateStr);
    if (isNaN(parsed.getTime())) {
      return dateStr;
    }
    return parsed.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      timeZone: 'UTC',
    });
  } catch {
    return dateStr;
  }
}

function formatShortDate(dateStr: string): string {
  try {
    const parsed = new Date(dateStr);
    if (isNaN(parsed.getTime())) {
      return dateStr;
    }
    return parsed.toLocaleDateString('es-ES', {
      month: 'short',
      day: 'numeric',
      timeZone: 'UTC',
    });
  } catch {
    return dateStr;
  }
}

const DailyActivityItem: React.FC<DailyActivityItemProps> = ({ day, maxEvents }) => {
  const commits = day.commits ?? 0;
  const issues = day.issues ?? 0;
  const prsOpened = day.pull_requests_opened ?? 0;
  const prsClosed = day.pull_requests_closed ?? 0;
  const releases = day.releases ?? 0;
  const totalDayEvents = commits + issues + prsOpened + prsClosed + releases;

  const barFillPercent = maxEvents > 0 ? Math.min(100, Math.round((totalDayEvents / maxEvents) * 100)) : 0;
  const commitsPercent = totalDayEvents > 0 ? (commits / totalDayEvents) * 100 : 0;
  const issuesPercent = totalDayEvents > 0 ? (issues / totalDayEvents) * 100 : 0;
  const prsPercent = totalDayEvents > 0 ? ((prsOpened + prsClosed) / totalDayEvents) * 100 : 0;
  const releasesPercent = totalDayEvents > 0 ? (releases / totalDayEvents) * 100 : 0;

  const dateFormatted = formatActivityDate(day.date);
  const shortDate = formatShortDate(day.date);

  return (
    <li className="activity-day-item">
      <article className="activity-day-card">
        <header className="activity-day-header">
          <div className="activity-day-title-group">
            <time dateTime={day.date} className="activity-day-date" title={`Fecha: ${day.date}`}>
              {dateFormatted}
            </time>
            <span className="activity-day-short-date" aria-hidden="true">
              {shortDate}
            </span>
          </div>
          <span className="activity-day-total-badge" aria-label={`Total de ${totalDayEvents} eventos este día`}>
            <strong>{totalDayEvents.toLocaleString()}</strong> {totalDayEvents === 1 ? 'evento' : 'eventos'}
          </span>
        </header>

        {/* Visual Bar representation using pure HTML + CSS */}
        <div
          className="activity-bar-container"
          role="img"
          aria-label={`Distribución de actividad del ${dateFormatted}: ${commits} commits, ${issues} issues, ${prsOpened + prsClosed} pull requests, ${releases} releases`}
        >
          <div className="activity-bar-track">
            <div className="activity-bar-fill" style={{ width: `${Math.max(barFillPercent, 4)}%` }}>
              {commitsPercent > 0 && (
                <div
                  className="activity-bar-segment segment-commits"
                  style={{ width: `${commitsPercent}%` }}
                  title={`Commits: ${commits}`}
                />
              )}
              {issuesPercent > 0 && (
                <div
                  className="activity-bar-segment segment-issues"
                  style={{ width: `${issuesPercent}%` }}
                  title={`Issues: ${issues}`}
                />
              )}
              {prsPercent > 0 && (
                <div
                  className="activity-bar-segment segment-prs"
                  style={{ width: `${prsPercent}%` }}
                  title={`Pull Requests: ${prsOpened + prsClosed} (${prsOpened} abiertos, ${prsClosed} cerrados)`}
                />
              )}
              {releasesPercent > 0 && (
                <div
                  className="activity-bar-segment segment-releases"
                  style={{ width: `${releasesPercent}%` }}
                  title={`Releases: ${releases}`}
                />
              )}
            </div>
          </div>
        </div>

        {/* Semantic textual metrics dl/dt/dd */}
        <dl className="activity-day-breakdown">
          <div className="activity-day-stat">
            <dt className="activity-day-stat-label">
              <span className="activity-dot commits" aria-hidden="true" />
              <span>Commits</span>
            </dt>
            <dd className="activity-day-stat-value">{commits.toLocaleString()}</dd>
          </div>

          <div className="activity-day-stat">
            <dt className="activity-day-stat-label">
              <span className="activity-dot issues" aria-hidden="true" />
              <span>Issues</span>
            </dt>
            <dd className="activity-day-stat-value">{issues.toLocaleString()}</dd>
          </div>

          <div className="activity-day-stat">
            <dt className="activity-day-stat-label">
              <span className="activity-dot prs" aria-hidden="true" />
              <span>PRs Abiertos</span>
            </dt>
            <dd className="activity-day-stat-value">{prsOpened.toLocaleString()}</dd>
          </div>

          <div className="activity-day-stat">
            <dt className="activity-day-stat-label">
              <span className="activity-dot prs-closed" aria-hidden="true" />
              <span>PRs Cerrados</span>
            </dt>
            <dd className="activity-day-stat-value">{prsClosed.toLocaleString()}</dd>
          </div>

          <div className="activity-day-stat">
            <dt className="activity-day-stat-label">
              <span className="activity-dot releases" aria-hidden="true" />
              <span>Releases</span>
            </dt>
            <dd className="activity-day-stat-value">{releases.toLocaleString()}</dd>
          </div>
        </dl>
      </article>
    </li>
  );
};

export const RepositoryActivityAnalysis: React.FC<RepositoryActivityAnalysisProps> = ({
  activity,
}) => {
  const dailyItems = activity?.daily ? [...activity.daily] : [];

  // Orden cronologico ascendente (del mas antiguo al mas reciente)
  const sortedDaily = dailyItems.sort((a, b) => {
    const timeA = new Date(a.date).getTime();
    const timeB = new Date(b.date).getTime();
    return timeA - timeB;
  });

  const totalCommits = activity?.total_commits ?? 0;
  const totalIssues = activity?.total_issues ?? 0;
  const totalPullRequests = activity?.total_pull_requests ?? 0;
  const totalReleases = activity?.total_releases ?? 0;

  const maxEventsPerDay = sortedDaily.reduce((max, day) => {
    const dayTotal =
      (day.commits ?? 0) +
      (day.issues ?? 0) +
      (day.pull_requests_opened ?? 0) +
      (day.pull_requests_closed ?? 0) +
      (day.releases ?? 0);
    return Math.max(max, dayTotal);
  }, 1);

  const hasActivityData = activity !== null && activity !== undefined && sortedDaily.length > 0;
  const daysCount = activity?.days ?? sortedDaily.length;
  const sinceFormatted = activity?.since ? formatActivityDate(activity.since) : null;
  const untilFormatted = activity?.until ? formatActivityDate(activity.until) : null;

  return (
    <section
      className="activity-section"
      id="repository-activity-analysis"
      aria-labelledby="activity-heading"
    >
      <div className="analyzer-container">
        <div className="activity-card">
          <header className="activity-header">
            <span className="repo-section-badge">Ritmo y Actividad</span>
            <div className="activity-title-row">
              <h2 id="activity-heading" className="activity-title">
                Actividad del Repositorio
              </h2>
            </div>
            <p className="activity-subtitle">
              {sinceFormatted && untilFormatted
                ? `Eventos registrados en los últimos ${daysCount} días (${sinceFormatted} – ${untilFormatted}).`
                : 'Distribución reciente de commits, issues, pull requests y releases.'}
            </p>
          </header>

          {/* Resumen metrico global dl/dt/dd */}
          <div className="activity-stats-container">
            <dl className="activity-stats-list">
              <div className="activity-stat-card">
                <dt className="activity-stat-label">
                  <span className="activity-dot commits" aria-hidden="true" />
                  <span>Commits</span>
                </dt>
                <dd className="activity-stat-value commits-text">{totalCommits.toLocaleString()}</dd>
              </div>

              <div className="activity-stat-card">
                <dt className="activity-stat-label">
                  <span className="activity-dot issues" aria-hidden="true" />
                  <span>Issues</span>
                </dt>
                <dd className="activity-stat-value issues-text">{totalIssues.toLocaleString()}</dd>
              </div>

              <div className="activity-stat-card">
                <dt className="activity-stat-label">
                  <span className="activity-dot prs" aria-hidden="true" />
                  <span>Pull Requests</span>
                </dt>
                <dd className="activity-stat-value prs-text">{totalPullRequests.toLocaleString()}</dd>
              </div>

              <div className="activity-stat-card">
                <dt className="activity-stat-label">
                  <span className="activity-dot releases" aria-hidden="true" />
                  <span>Releases</span>
                </dt>
                <dd className="activity-stat-value releases-text">{totalReleases.toLocaleString()}</dd>
              </div>
            </dl>
          </div>

          {/* Listado diario con barras HTML/CSS */}
          {!hasActivityData ? (
            <div className="activity-empty" role="status">
              <p className="repo-text-muted">
                No se registró actividad diaria en el periodo analizado.
              </p>
            </div>
          ) : (
            <div className="activity-daily-section">
              <h3 className="activity-daily-title">Actividad Diaria Cronológica</h3>
              <ul className="activity-daily-list" aria-label="Lista de actividad diaria cronológica">
                {sortedDaily.map((day, index) => (
                  <DailyActivityItem
                    key={`${day.date}-${index}`}
                    day={day}
                    maxEvents={maxEventsPerDay}
                  />
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};
