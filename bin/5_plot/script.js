/* jshint esversion: 6 */

//--Initialize data and make the initial plot
//Get root element
const canvas = {
    width: 960,
    height: 500,
    color: d3.schemePaired
  };
let root = d3
    .select("svg")
    .attr("width", canvas.width)
    .attr("height", canvas.height)
    .style("box-shadow", "1px 2px 4px #BFBFBF");
  root
    .insert("g")
    .classed("contour-plot", true)
    .attr("stroke", "#FFFFFF")
    .attr("stroke-width", 0.5)
    .attr("stroke-linejoin", "round");
  root
    .insert("g")
    .classed("scatter-plot", true);

//Get data and create initial plot
d3.json("./person_prefpoint.json").then(result => {
  data = result;
  plot("yu");
});


//--Plotting
function plot(targetName) {

  //Title
  root
    .append("text")
    .attr("x", canvas.width / 8)
    .attr("y", canvas.height / 4)
    .attr("text-anchor", "left")
    .style("font-size", "16px")
    .text(targetName + "'s Graph");


  //--Contour plot
  //Initialization
  let contourPlot = {
    data: data.point[targetName],
    color: d3.scaleSequential(d3.interpolateYlGnBu).domain([0, 0.05]),
    x: d3
      .scaleLinear()
      .domain([-100, 100])
      .rangeRound([0, canvas.width]),
    y: d3
      .scaleLinear()
      .domain([-100, 100])
      .rangeRound([0, canvas.height]),
    contour: d3
      .contourDensity()
      .x(d => contourPlot.x(d[0]))
      .y(d => contourPlot.y(d[1]))
      .size([canvas.width, canvas.height])
      .bandwidth(10)
      .thresholds(8)
  };

  //Implement
  geoPaths = root
    .select(".contour-plot")
    .selectAll("path")
    .style("opacity", 0)
    .data(contourPlot.contour(contourPlot.data));
  geoPaths
    .enter()
    .append("path")
    .attr("fill", d => contourPlot.color(d.value))
    .attr("d", d3.geoPath())
    .style("opacity", 0)
    .transition()
    .duration(800)
    .style("opacity", 0.4);
  geoPaths
    .exit()
    .transition()
    .duration(800)
    .style("opacity", 0)
    .remove();
  geoPaths
    .transition()
    .duration(1200)
    .ease(d3.easeCubicOut)
    .style("opacity", 0.4)
    .attr("d", d3.geoPath())


  //--Scatter plot
  //Initialization
  let scatterPlot = {
    data: data.coordinate,
    color: d3.schemeAccent,
    x: d3
      .scaleLinear()
      .domain([-100, 100])
      .rangeRound([0, canvas.width]),
    y: d3
      .scaleLinear()
      .domain([-100, 100])
      .rangeRound([0, canvas.height])
  };

  //Implement
  root
    .select(".scatter-plot")
    .selectAll("circle")
    .data(scatterPlot.data)
    .enter()
    .append("circle")
    .attr("r", 2)
    .attr("cx", d => scatterPlot.x(d[0]))
    .attr("cy", d => scatterPlot.y(d[1]))
    .style("fill", scatterPlot.color[7])
    .style("stroke", "#FFFFFF")
    .on("mouseover", (d, i, nodes) => {
      d3.select(nodes[i])
        .transition()
        .duration(200)
        .style("r", 4)
        .style("fill", scatterPlot.color[2]);
      d3.select("#scatter-tooltip")
        .transition()
        .duration(200)
        .style("opacity", "0.9");
      d3.select("#scatter-tooltip")
        .html(data.topic[i])
        .style("visibility", "visible")
        .style("left", d3.event.pageX + 5 + "px")
        .style("top", d3.event.pageY - 28 + "px");
    })
    .on("mouseout", (d, i, nodes) => {
      d3.select(nodes[i])
        .transition()
        .duration(500)
        .style("r", 2)
        .style("fill", scatterPlot.color[7]);
      let p = new Promise((resolve, reject) => {
        d3.select("#scatter-tooltip")
          .transition()
          .duration(500)
          .style("opacity", "0")
          .on("end", resolve);
      });
      p.then(() => {
        d3.select("#scatter-tooltip")
          .style("visibility", "hidden");
      });
    });
}

$("#target-jian").click(() => {
  plot("jian");
});
$("#target-yu").click(() => {
  plot("yu");
});
