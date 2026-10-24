if (typeof Map.groupBy !== "function") {
  Object.defineProperty(Map, "groupBy", {
    configurable: true,
    writable: true,
    value(items, keySelector) {
      const groups = new Map();
      let index = 0;

      for (const item of items) {
        const key = keySelector(item, index++);
        const group = groups.get(key);
        if (group) group.push(item);
        else groups.set(key, [item]);
      }

      return groups;
    },
  });
}
