// Keyset pagination. The cursor is the last sort key, not a skip count.
(function (root) {
  function keysetPage(rows, cursor, size, key) {
    key = key || function (row) { return row.civic_id; };
    var n = Math.max(1, Number(size) || 20);
    var rest = cursor == null ? rows : rows.filter(function (row) { return key(row) > cursor; });
    var page = rest.slice(0, n);
    var next = rest.length > n && page.length ? key(page[page.length - 1]) : null;
    return {
      page: page,
      cursor: page.length ? key(page[page.length - 1]) : cursor,
      nextCursor: next,
      hasMore: next != null,
      start: page.length ? key(page[0]) : null
    };
  }

  function previousCursor(rows, firstKey, size, key) {
    key = key || function (row) { return row.civic_id; };
    var before = rows.filter(function (row) { return key(row) < firstKey; });
    if (!before.length) return null;
    var start = Math.max(0, before.length - Math.max(1, Number(size) || 20));
    var prev = before.slice(start);
    var index = rows.findIndex(function (row) { return key(row) === key(prev[0]); });
    return index <= 0 ? null : key(rows[index - 1]);
  }

  root.Keyset = { keysetPage: keysetPage, previousCursor: previousCursor };
})(window);
