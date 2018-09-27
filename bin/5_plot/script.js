d3.json("person_pref.json").then(data => {
  // Populate a grid of n×m values where -2 ≤ x ≤ 2 and -2 ≤ y ≤ 1.
  var n = 240,
    m = 125,
    values = data.pref.jian;
  console.log(values);

  var svg = d3
      .select("svg")
      .attr("stroke", "#000")
      .attr("stroke-width", 0.5),
    width = +svg.attr("width"),
    height = +svg.attr("height");

  var thresholds = d3.range(1, 10).map(function(p) {
    return Math.pow(2, p);
  });

  var contours = d3
    .contours()
    .size([n, m])
    .thresholds(d3.range(1, 10));

  var color = d3
    .scaleLog()
    .domain(d3.extent(thresholds))
    .interpolate(function() {
      return d3.interpolateYlGnBu;
    });

  svg
    .selectAll("path")
    .data(contours(values))
    .enter()
    .append("path")
    .attr("d", d3.geoPath(d3.geoIdentity().scale(width / n)))
    .attr("fill", function(d) {
      return color(d.value);
    });
});
