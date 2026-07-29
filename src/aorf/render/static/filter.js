/* Two small behaviours, no dependencies: filter a table, and sort one.
   Served from the same origin as a file rather than inlined, so the page's Content-Security
   -Policy can stay `script-src 'self'` with no unsafe-inline and no nonce plumbing. */

(function () {
  "use strict";

  function filterRows(table, query) {
    var needle = query.trim().toLowerCase();
    var rows = table.tBodies.length ? table.tBodies[0].rows : [];
    for (var i = 0; i < rows.length; i++) {
      var text = (rows[i].textContent || "").toLowerCase();
      rows[i].hidden = needle !== "" && text.indexOf(needle) === -1;
    }
  }

  document.querySelectorAll("input.filter[data-filter-target]").forEach(function (input) {
    var table = document.querySelector(input.getAttribute("data-filter-target"));
    if (!table) return;
    input.addEventListener("input", function () {
      filterRows(table, input.value);
    });
  });

  /* Sort a column, numerically when every cell in it parses as a number. A column of
     metrics sorted as text would put 0.9 above 0.71, which is worse than not sorting. */
  function cellValue(row, index) {
    var cell = row.cells[index];
    return cell ? (cell.textContent || "").trim() : "";
  }

  document.querySelectorAll("table.sortable").forEach(function (table) {
    var headers = table.tHead ? table.tHead.rows[0].cells : [];
    Array.prototype.forEach.call(headers, function (th, index) {
      th.style.cursor = "pointer";
      th.title = "Sort by " + (th.textContent || "").trim();
      var descending = false;
      th.addEventListener("click", function () {
        var body = table.tBodies[0];
        if (!body) return;
        var rows = Array.prototype.slice.call(body.rows);
        var numeric = rows.every(function (row) {
          var v = cellValue(row, index);
          return v === "" || !isNaN(parseFloat(v));
        });
        rows.sort(function (a, b) {
          var x = cellValue(a, index);
          var y = cellValue(b, index);
          if (numeric) {
            var nx = parseFloat(x);
            var ny = parseFloat(y);
            if (isNaN(nx)) nx = -Infinity;
            if (isNaN(ny)) ny = -Infinity;
            return descending ? ny - nx : nx - ny;
          }
          return descending ? y.localeCompare(x) : x.localeCompare(y);
        });
        rows.forEach(function (row) {
          body.appendChild(row);
        });
        descending = !descending;
      });
    });
  });
})();
