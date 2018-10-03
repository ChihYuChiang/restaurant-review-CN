/* jshint esversion: 6 */

//--Initialize data and make the initial plot
//Shared info
var canvas = {
  width: window.innerWidth,
  height: window.innerHeight * 0.8,
  color_contour: d3.scaleSequential(d3.interpolateYlGnBu).domain([0, 0.05]),
  color_scatter: d3.schemeAccent,
  color_theme: d3.schemeCategory10,
  scale_x: d3.scaleLinear(),
  scale_y: d3.scaleLinear(),
  translate_x: 0,
  translate_y: 0,
  scale: 1,
  data: []
};

//Setup root element
let root = d3
    .select("svg")
    .attr("width", canvas.width)
    .attr("height", canvas.height)
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
  root
    .insert("rect")
    .classed("click-listener", true)
    .attr('width', canvas.width)
    .attr('height', canvas.height)
    .style('opacity', 0)
    .style("visibility", "hidden");

//Get data and create initial plot
d3.json("./person_prefpoint.json").then(result => {
  canvas.data = result;
  canvas.scale_x.domain(canvas.data.coordinateRange[0]).rangeRound([0, canvas.width]);
  canvas.scale_y.domain(canvas.data.coordinateRange[1]).rangeRound([0, canvas.height]);
  plot("yu");
});


//--Plotting
function plot(targetName) {

  //--Click listener
  d3.select(".click-listener")
    .on("click", () => {
      let p = new Promise((resolve, reject) => {
        root.select(".click-listener").style("pointer-events", "none");
        root.selectAll("g")
          .transition()
          .duration(1200)
          .attr("transform", 'translate(' + 0 + ', ' + 0 + ')scale(' + 1 + ')')
          .on("end", resolve);
        Tip.hideAll();
      });
      p.then(() => {
        d3.select("#btn-pref").style("visibility", "visible");
        d3.select("#btn-info").style("visibility", "visible");
        root.select(".click-listener").style("visibility", "hidden");
      });
      canvas.translate_x = 0;
      canvas.translate_y = 0;
      canvas.scale = 1;
    });


  //--Title
  d3.select("#plot-title")
    .text(' - ' + targetName[0].toUpperCase() + targetName.slice(1, targetName.length) + "'s Graph")
    .style("opacity", 0)
    .transition()
    .duration(600)
    .style("opacity", 1);


  //--Contour plot
  //Initialization
  let contourPlot = {
    data: canvas.data.point[targetName],
    contour: d3
      .contourDensity()
      .x(d => canvas.scale_x(d[0]))
      .y(d => canvas.scale_y(d[1]))
      .size([canvas.width, canvas.height])
      .bandwidth(10)
      .thresholds(8)
  };

  //Implement
  let geoPaths = root
    .select(".contour-plot")
    .selectAll("path")
    .style("opacity", 0)
    .data(contourPlot.contour(contourPlot.data));
  geoPaths.enter()
    .append("path")
    .attr("fill", d => canvas.color_contour(d.value))
    .attr("d", d3.geoPath())
    .style("opacity", 0)
    .transition()
    .duration(800)
    .style("opacity", 0.4);
  geoPaths.exit()
    .transition()
    .duration(800)
    .style("opacity", 0)
    .remove();
  geoPaths
    .transition()
    .duration(1200)
    .ease(d3.easeCubicOut)
    .style("opacity", 0.4)
    .attr("d", d3.geoPath());


  //--Scatter plot
  //Initialization
  let scatterPlot = {
    pref: canvas.data.pref[targetName],
    tip: {
      main: new Tip("scatter-tooltip-main"),
      s1: new Tip("scatter-tooltip-s1", 0),
      s2: new Tip("scatter-tooltip-s2", 1),
      s3: new Tip("scatter-tooltip-s3", 2),
      s4: new Tip("scatter-tooltip-s4", 3),
      s5: new Tip("scatter-tooltip-s5", 4)
    },
    getTranslate: (tx, ty) => [
      (canvas.width/2 - tx) * canvas.scale - canvas.width/2 * (canvas.scale - 1),
      (canvas.height/2 - ty) * canvas.scale - canvas.height/2 * (canvas.scale - 1)
    ],
    getRefLocation: (tx, ty, rElement) => [
      canvas.width/2 + (+d3.select(rElement).attr("cx") - tx) * canvas.scale + 35,
      canvas.height/2 + (+d3.select(rElement).attr("cy") - ty) * canvas.scale - 25
    ],
    genTipContent: (topic, pref) => {
      let content = topic + '<br><i class="fas fa-star icon-star"></i> ' + (pref ? pref : 'Haven\'t visited');
      return content;
    },
  };

  //Implement
  let circles = root
    .select(".scatter-plot")
    .selectAll("circle")
    .data(canvas.data.coordinate);
  circles
    .enter()
    .append("circle")
    .attr("r", 2)
    .attr("cx", d => canvas.scale_x(d[0]))
    .attr("cy", d => canvas.scale_y(d[1]))
    .style("fill", canvas.color_scatter[7])
    .style("stroke", "#FFFFFF")
    .merge(circles)
    .on("mouseover", (d, i, nodes) => {
      let [tx, ty] = d3.mouse(root.node());
      d3.select(nodes[i])
        .style("cursor", "pointer")
        .transition()
        .duration(200)
        .style("r", 6)
        .style("fill", canvas.color_scatter[2]);
      const tipContent = scatterPlot.genTipContent(canvas.data.topic[i], scatterPlot.pref[i]);
      const tipCoordinate = [tx + 25, ty - 28];
      scatterPlot.tip.main.show();
      scatterPlot.tip.main.setContent8MoveTo(tipContent, tipCoordinate);
    })
    .on("mouseout", (d, i, nodes) => {
      d3.select(nodes[i])
        .transition()
        .duration(500)
        .style("r", 2)
        .style("fill", canvas.color_scatter[7]);
      scatterPlot.tip.main.hide();
    })
    .on("click", (d, i, nodes) => {
      d3.select("#btn-pref").style("visibility", "hidden");
      d3.select("#btn-info").style("visibility", "hidden");
      d3.select(nodes[i]).style("stroke", canvas.color_theme[1]);
      let [tx, ty] = [d3.select(nodes[i]).attr("cx"), d3.select(nodes[i]).attr("cy")];
      canvas.scale = 5;
      [canvas.translate_x, canvas.translate_y] = scatterPlot.getTranslate(tx, ty);
      root.select(".click-listener")
        .style("visibility", "visible")
        .style("pointer-events", "all");
      let p = new Promise((resolve, reject) => {
        root.selectAll("g")
          .transition()
          .duration(1000)
          .attr("transform", 'translate(' + canvas.translate_x + ', ' + canvas.translate_y + ')scale(' + canvas.scale + ')')
          .on("end", resolve);
      });
      p.then(() => {
        const tipContent_main = scatterPlot.genTipContent(canvas.data.topic[i], scatterPlot.pref[i]);
        const tipCoordinate_main = [canvas.width/2 + 35, canvas.height/2 - 25];
        scatterPlot.tip.main.setContent8MoveTo(tipContent_main, tipCoordinate_main);
        
        const rIds = canvas.data.closestneighbor[i];
        const tipContent_sub = rIds.map((id) => scatterPlot.genTipContent(canvas.data.topic[id], scatterPlot.pref[id]));
        const tipCoordinate_sub = rIds.map((id) => scatterPlot.getRefLocation(tx, ty, nodes[id]));
        for(const key in scatterPlot.tip) {
          let tip = scatterPlot.tip[key];
          if(tip.bindSub !== null) { tip.setContent8MoveTo(tipContent_sub[tip.bindSub], tipCoordinate_sub[tip.bindSub]); }
        }
        
        Tip.showAll();
      });
    });
}


//--Tip operations
class Tip {
  constructor(tipId, bindSub=null) {
    this.id = '#' + tipId;
    this.bindSub = bindSub;
  }

  static showAll() {
    d3.selectAll(".tooltip")
      .transition()
      .duration(200)
      .style("opacity", "0.9")
      .style("background-color", "#FFFFFF");
  }
  static hideAll() {
    d3.selectAll(".tooltip")
      .transition()
      .duration(500)
      .style("opacity", "0");
  }
  
  show(bgColor="#FFFFFF") {
    d3.select(this.id)
      .transition()
      .duration(200)
      .style("opacity", "0.9")
      .style("background-color", bgColor);
  }
  hide() {
    d3.select(this.id)
      .transition()
      .duration(500)
      .style("opacity", "0")
  }
  setContent8MoveTo(content, coordinate) {
    d3.select(this.id)
      .html(content)
      .style("left", coordinate[0] + "px")
      .style("top", coordinate[1] + "px");
  }
}


//--Bind target selection
d3.select("#target-yu")
  .on("click", () => {plot("yu");});
d3.select("#target-jian")
  .on("click", () => {plot("jian");});
d3.select("#target-xin")
  .on("click", () => {plot("xin");});


//--Open instruction by default
$('document').ready(() => {
  setTimeout(() => {
    $('#info').modal('show');
  }, 1500);
})