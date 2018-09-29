d3.json("person_prefpoint.json").then(data => {

  var values = data.point.jian;

  var svg = d3.select("svg"),
      width = +svg.attr("width"),
      height = +svg.attr("height");

  var color = d3.scaleSequential(d3.interpolateYlGnBu)
    .domain([0, 0.05]);

  var x = d3.scaleLinear()
    .domain([-100, 100])
    .rangeRound([0, width]);

  var y = d3.scaleLinear()
    .domain([-100, 100])
    .rangeRound([0, height]);

  var contours = d3
    .contourDensity()
    .x((d) => x(d[0]))
    .y((d) => y(d[1]))
    .size([width, height])
    .bandwidth(10);

  svg.insert("g")
    .attr("stroke", "#FFFFFF")
    .attr("stroke-width", 0.5)
    .attr("stroke-linejoin", "round")
    .selectAll("path")
    .data(contours(values))
    .enter()
    .append("path")
    .attr("fill", (d) => color(d.value))
    .attr("d", d3.geoPath());

  // svg.insert("g")
  //   .selectAll(".dot")
  //   .data(data)
  //   .enter().append("circle")
  //   .attr("class", "dot")
  //   .attr("r", 3.5)
  //   .attr("cx", xMap)
  //   .attr("cy", yMap)
  //   .style("fill", function (d) { return color(cValue(d)); })
  //   .on("mouseover", function (d) {
  //     tooltip.transition()
  //       .duration(200)
  //       .style("opacity", .9);
  //     tooltip.html(d["Cereal Name"] + "<br/> (" + xValue(d)
  //       + ", " + yValue(d) + ")")
  //       .style("left", (d3.event.pageX + 5) + "px")
  //       .style("top", (d3.event.pageY - 28) + "px");
  //   })
  //   .on("mouseout", function (d) {
  //     tooltip.transition()
  //       .duration(500)
  //       .style("opacity", 0);
  //   });
});
