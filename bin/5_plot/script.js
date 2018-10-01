/* jshint esversion: 6 */

//--Initialize data and make the initial plot
//Shared info
var canvas = {
  width: 960,
  height: 500,
  color_contour: d3.scaleSequential(d3.interpolateYlGnBu).domain([0, 0.05]),
  color_scatter: d3.schemeAccent,
  translate_x: 0,
  translate_y: 0,
  scale: 1
};
canvas.xScale = d3.scaleLinear().domain([-100, 100]).rangeRound([0, canvas.width]);
canvas.yScale = d3.scaleLinear().domain([-100, 100]).rangeRound([0, canvas.height]);

//Setup root element
let root = d3
    .select("svg")
    .attr("width", canvas.width)
    .attr("height", canvas.height)
    .style("box-shadow", "1px 2px 4px #BFBFBF")
    .style("background-color", "#FCFCFC");
  root
    .append("g")
    .classed("contour-plot", true)
    .attr("stroke", "#FFFFFF")
    .attr("stroke-width", 0.5)
    .attr("stroke-linejoin", "round");
  root
    .append("g")
    .classed("scatter-plot", true);
  root
    .append("text")
    .attr("x", canvas.width / 8)
    .attr("y", canvas.height / 4)
    .attr("text-anchor", "left")
    .style("font-size", "16px");
  root.insert("rect")
    .classed("click-listener", true)
    .attr('width', canvas.width)
    .attr('height', canvas.height)
    .style('opacity', 0)
    .style("visibility", "hidden")
    .on("click", () => {
      root.select(".click-listener").style("visibility", "hidden");
      root.selectAll("g")
        .transition()
        .duration(1000)
        .attr("transform", 'translate(' + 0 + ', ' + 0 + ')scale(' + 1 + ')');
      canvas.translate_x = 0;
      canvas.translate_y = 0;
      canvas.scale = 1;
    });

//Get data and create initial plot
d3.json("./person_prefpoint.json").then(result => {
  data = result;
  plot("yu");
});


//--Plotting
function plot(targetName) {

  //Title
  d3
    .select("#plot-title")
    .text(" - " + targetName + "'s Graph")
    .style("opacity", 0)
    .transition()
    .duration(600)
    .style("opacity", 1);


  //--Contour plot
  //Initialization
  let contourPlot = {
    data: data.point[targetName],
    contour: d3
      .contourDensity()
      .x(d => canvas.xScale(d[0]))
      .y(d => canvas.yScale(d[1]))
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
    .attr("fill", d => canvas.color_contour(d.value))
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
  };

  //Implement
  root
    .select(".scatter-plot")
    .selectAll("circle")
    .data(scatterPlot.data)
    .enter()
    .append("circle")
    .attr("r", 2)
    .attr("cx", d => canvas.xScale(d[0]))
    .attr("cy", d => canvas.yScale(d[1]))
    .style("fill", canvas.color_scatter[7])
    .style("stroke", "#FFFFFF")
    .on("mouseover", (d, i, nodes) => {
      d3.select(nodes[i])
        .style("cursor", "pointer")
        .transition()
        .duration(200)
        .style("r", 6)
        .style("fill", canvas.color_scatter[2]);
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
        .style("fill", canvas.color_scatter[7]);
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
    })
    .on("click", () => {
      let [tx, ty] = d3.mouse(root.node());
      canvas.scale = 3;
      canvas.translate_x = (canvas.width/2 - tx) * canvas.scale - canvas.width/2 * (canvas.scale - 1) ;
      canvas.translate_y = (canvas.height/2 - ty) * canvas.scale - canvas.height/2 * (canvas.scale - 1);
      root.selectAll("g")
        .transition()
        .duration(1000)
        .attr("transform", 'translate(' + canvas.translate_x + ', ' + canvas.translate_y + ')scale(' + canvas.scale + ')');
      root.select(".click-listener")
        .style("visibility", "visible")
    });
}

$("#target-jian").click(() => {
  plot("jian");
});
$("#target-yu").click(() => {
  plot("yu");
});
