const { groupBy, toPairs, head, values, pluck } = require("ramda");

const versions = {
  3.16: {
    python: ["3.10", "3.11", "3.12", "3.13"],
    django: ["4.2", "5.0", "5.1", "5.2"],
  },
  3.15: {
    python: ["3.10", "3.11", "3.12"],
    django: ["4.0", "4.1", "4.2", "5.0"],
  },
  3.14: {
    python: ["3.10", "3.11"],
    django: ["4.0", "4.1"],
  },
  3.13: {
    python: ["3.10", "3.11"],
    django: ["4.0"],
  },
};

const matrix = toPairs(versions).flatMap(([drf, { python, django }]) =>
  python.flatMap((python) =>
    django.map((django) => ({
      python,
      django,
      drf,
    })),
  ),
);

const groups = values(
  groupBy(({ python, django }) => [python, django].join("-"))(matrix),
);

const environments = groups.map((group) => {
  const [{ python, django }] = group;
  const drf = pluck("drf", group);

  return [
    "py".concat(python),
    "django".concat(django),
    drf.length > 1 ? `drf{${drf.join(",")}}` : "drf".concat(drf[0]),
  ]
    .join("-")
    .replaceAll(".", "");
});

console.log(
    environments
    .sort()
    .join("\n")
);
