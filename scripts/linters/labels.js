import { DateTime, Duration } from "luxon";
import { Octokit } from "octokit";

const token = process.env.GITHUB_TOKEN;
const [owner, repo] = process.env.GITHUB_REPOSITORY.split("/");
const { rest, paginate } = new Octokit({ auth: token });

const now = DateTime.now();

(async () => {
  for await (const { data: issues } of paginate.iterator(
    rest.issues.listForRepo,
    { owner, repo }
  )) {
    issues.forEach((issue) => {
      const { number, created_at, title, pull_request, html_url } = issue;
      const assignee = issue.assignee?.login;

      const age = now
        .diff(DateTime.fromISO(created_at))
        .shiftTo("years", "months", "days")
        .toHuman({ maximumFractionDigits: 0 });

      const labels = issue.labels.map(({ name }) => name);
      const version = labels.find((name) => /\d+\.[\dx]+\.[\dx]+/.test(name));

      const triage = labels.includes("triage");
      const help = labels.includes("help wanted");

      const question = labels.includes("question");
      const unanswered = labels.includes("unanswered");

      const directions = labels.filter((i) =>
        ["bug", "enhancement", "question"].includes(i)
      );

      const problems = [];

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
        if (triage && version) {
          problems.push('Should not have both a "triage" and version label');
        }

        if (!triage && !version) {
          problems.push('Missing a "triage" or version label');
        }
      } else {
        if ([triage, question, version].filter((i) => i).length > 1) {
          problems.push('Too many "triage", "question" and version labels');
        }

        if ([triage, question, version].every((i) => !i)) {
          problems.push('Missing a "triage", "question" or version label');
        }
      }

      if (!triage) {
        if (directions.length === 0) {
          problems.push('Missing a "bug", "enhancement" or "question" label');
        }

        if (directions.length > 1) {
          problems.push('Too many "bug", "enhancement" and "question" labels');
        }
      }

      if (problems.length > 0) {
        console.log({
          age,
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
            triage,
            question,
            unanswered,
            directions,
          },
        });
      }
    });
  }
})();
