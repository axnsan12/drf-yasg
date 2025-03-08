import { DateTime, Duration } from "luxon";
import { Octokit } from "octokit";

const token = process.env.GITHUB_TOKEN;
const [owner, repo] = process.env.GITHUB_REPOSITORY.split("/");
const { rest, paginate } = new Octokit({ auth: token });

const now = DateTime.now();
const age = (timestamp) => now.diff(DateTime.fromISO(timestamp));

(async () => {
  for await (const { data: issues } of paginate.iterator(
    rest.issues.listForRepo,
    { owner, repo }
  )) {
    issues
      .filter(
        ({ created_at }) => age(created_at) < Duration.fromObject({ years: 1 })
      )
      .forEach((issue) => {
        const { number, created_at, title, pull_request, html_url } = issue;
        const assignee = issue.assignee?.login;

        const labels = issue.labels.map(({ name }) => name);
        const version = labels.find((name) => /\d+\.[\dx]+\.[\dx]+/.test(name));

        const triaged = labels.includes("triage");
        const help = labels.includes("help wanted");

        const question = labels.includes("question");
        const unanswered = labels.includes("unanswered");

        const directions = labels.filter((i) =>
          ["bug", "enhancement", "question"].includes(i)
        );

        const problems = [];

        if (directions.length === 0) {
          problems.push('Missing a "bug", "enhancement" or "question" label');
        }

        if (directions.length > 1) {
          problems.push('Too many "bug", "enhancement" and "question" labels');
        }

        if (version) {
          if (assignee && help) {
            problems.push(
              'Should not have both an assignee and a "help wanted" label'
            );
          }

          if (!assignee && !help) {
            problems.push('Missing an assignee or a "help wanted" label');
          }
        } else {
          if (assignee || help) {
            problems.push("Missing a version label");
          }
        }

        if (pull_request) {
          if (triaged && version) {
            problems.push('Should not have both a "triage" and version label');
          }

          if (!triaged && !version) {
            problems.push('Missing a "triage" or version label');
          }
        } else {
          if ([triaged, question, version].filter((i) => i).length > 1) {
            problems.push('Too many "triage", "question" and version labels');
          }

          if ([triaged, question, version].every((i) => !i)) {
            problems.push('Missing a "triage", "question" or version label');
          }
        }

        if (problems.length > 0) {
          console.log({
            age: age(created_at)
              .shiftTo("years", "months", "days")
              .toHuman({ maximumFractionDigits: 0 }),
            source: {
              id: number,
              title,
              url: html_url,
            },
            problems,
            context: {
              labels,
              assignee,
              version,
              help_wanted: help,
              triaged,
              question,
              unanswered,
              directions,
            },
          });
        }
      });
  }
})();
