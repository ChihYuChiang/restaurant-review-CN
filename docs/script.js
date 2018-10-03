/* jshint esversion: 6 */

/*
------------------------------------------------------------
Initialize data and make the initial plot
------------------------------------------------------------
*/

//--Canvas store
var canvas = {
  width: window.innerWidth - 40,
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


//--Setup element structure
//Root svg
let root = d3
    .select("svg")
    .attr("width", canvas.width)
    .attr("height", canvas.height)
    .style("background-color", "#FCFCFC");
  
//Contour plot group
root
  .append("g")
  .classed("contour-plot", true)
  .attr("stroke", "#FFFFFF")
  .attr("stroke-width", 0.5)
  .attr("stroke-linejoin", "round");

//Scatter plot group
root
  .append("g")
  .classed("scatter-plot", true);

//Click listener on top of the canvas
root
  .insert("rect")
  .classed("click-listener", true)
  .attr('width', canvas.width)
  .attr('height', canvas.height)
  .style('opacity', 0)
  .style("visibility", "hidden");


//--Get data and create initial plot
d3.json("./person_prefpoint.json").then(result => {
  canvas.data = result;
  canvas.scale_x.domain(canvas.data.coordinateRange[0]).rangeRound([0, canvas.width]);
  canvas.scale_y.domain(canvas.data.coordinateRange[1]).rangeRound([0, canvas.height]);
  plot("yu");
});




/*
------------------------------------------------------------
Plotting
------------------------------------------------------------
*/

function plot(targetName) {

  //--Click listener for zooming
  d3.select(".click-listener")
    .on("click", () => {
      let p = new Promise((resolve, reject) => {
        //Toggle the listener
        root.select(".click-listener").style("pointer-events", "none");
        
        //Reset the transformation (zoom out)
        root.selectAll("g")
        .transition()
        .duration(1200)
        .attr("transform", 'translate(' + 0 + ', ' + 0 + ')scale(' + 1 + ')')
        .on("end", resolve);
        
        //Hide all tips
        Tip.hideAll();
      });
      p.then(() => {
        //Toggle the control buttons
        d3.select("#btn-pref").style("visibility", "visible");
        d3.select("#btn-info").style("visibility", "visible");

        //Toggle the listener
        root.select(".click-listener").style("visibility", "hidden");
      });

      //Record the current canvas transformation
      canvas.translate_x = 0;
      canvas.translate_y = 0;
      canvas.scale = 1;
    });


  //--Plot title
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
      .bandwidth(12)
      .thresholds(15)
  };

  //Select the path elements and bind data
  //Update selection 1
  let geoPaths = root
    .select(".contour-plot")
    .selectAll("path")
    .style("opacity", 0)
    .data(contourPlot.contour(contourPlot.data));
  
  //Enter selection (create circles)
  geoPaths.enter()
    .append("path")
    .attr("fill", d => canvas.color_contour(d.value))
    .attr("d", d3.geoPath())
    .style("opacity", 0)
    .transition()
    .duration(800)
    .style("opacity", 0.4);

  //Exit selection
  geoPaths.exit()
    .transition()
    .duration(800)
    .style("opacity", 0)
    .remove();
  
  //Update selection 2
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

    //Tip elements
    tip: {
      main: new Tip("scatter-tooltip-main"),
      s1: new Tip("scatter-tooltip-s1", 0),
      s2: new Tip("scatter-tooltip-s2", 1),
      s3: new Tip("scatter-tooltip-s3", 2),
      s4: new Tip("scatter-tooltip-s4", 3),
      s5: new Tip("scatter-tooltip-s5", 4)
    },

    //To be offset from the circle
    tipAdjustment: { x: 25, y: -28 },

    //Compute the translation when click and focus on a circle
    getTranslate: (tx, ty) => [
      (canvas.width/2 - tx) * canvas.scale - canvas.width/2 * (canvas.scale - 1),
      (canvas.height/2 - ty) * canvas.scale - canvas.height/2 * (canvas.scale - 1)
    ],

    //Compute the locations of reference circles for attaching the tips
    getRefLocation: (tx, ty, rElement) => [
      canvas.width/2 + (+d3.select(rElement).attr("cx") - tx) * canvas.scale + scatterPlot.tipAdjustment.x,
      canvas.height/2 + (+d3.select(rElement).attr("cy") - ty) * canvas.scale + scatterPlot.tipAdjustment.y
    ],

    //Generate tip content
    genTipContent: (topic, pref) => {
      let content = topic + '<br><i class="fas fa-star icon-star"></i> ' + (pref ? pref : 'Haven\'t visited');
      return content;
    },
  };

  //Select the circles and bind data
  //Update selection
  let circles = root
    .select(".scatter-plot")
    .selectAll("circle")
    .data(canvas.data.coordinate);
  
  //Enter selection
  circles
    .enter()
    .append("circle")
    .attr("r", 2.5)
    .attr("cx", d => canvas.scale_x(d[0]))
    .attr("cy", d => canvas.scale_y(d[1]))
    .style("fill", canvas.color_scatter[7])
    .style("stroke", "#FFFFFF")

    //Merge the enter selection with the update selection
    .merge(circles)
    
    //Event listeners
    //The event listeners will be reattached for both entering circles and updating circles
    .on("mouseover", (d, i, nodes) => {
      //Get the event coordinate
      let [tx, ty] = d3.mouse(root.node());

      //Update circle appearance
      d3.select(nodes[i])
        .style("cursor", "pointer")
        .transition()
        .duration(200)
        .attr("r", 8)
        .style("fill", canvas.color_scatter[2]);
      
      //Show tip at proper location
      const tipContent = scatterPlot.genTipContent(canvas.data.topic[i], scatterPlot.pref[i]);
      const tipCoordinate = [tx + scatterPlot.tipAdjustment.x - 8, ty + scatterPlot.tipAdjustment.y];
      scatterPlot.tip.main.show();
      scatterPlot.tip.main.setContent8MoveTo(tipContent, tipCoordinate);
    })

    .on("mouseout", (d, i, nodes) => {
      //Update circle appearance
      d3.select(nodes[i])
        .transition()
        .duration(500)
        .attr("r", 2.5)
        .style("fill", canvas.color_scatter[7]);
      
      //Hide all tips
      scatterPlot.tip.main.hide();
    })

    .on("click", (d, i, nodes) => {
      //Toggle the control buttons
      d3.select("#btn-pref").style("visibility", "hidden");
      d3.select("#btn-info").style("visibility", "hidden");

      //Update circle appearance
      d3.select(nodes[i]).style("stroke", canvas.color_theme[1]);

      //Toggle the listener
      root.select(".click-listener")
        .style("visibility", "visible")
        .style("pointer-events", "all");
      
      //Get the location of the clicked circle
      let [tx, ty] = [d3.select(nodes[i]).attr("cx"), d3.select(nodes[i]).attr("cy")];
      
      //Based on the circle location, zoom in the canvas
      //(Scale up both the contour and scatter plots)
      canvas.scale = 5;
      [canvas.translate_x, canvas.translate_y] = scatterPlot.getTranslate(tx, ty);
      let p = new Promise((resolve, reject) => {
        root.selectAll("g")
          .transition()
          .duration(1000)
          .attr("transform", 'translate(' + canvas.translate_x + ', ' + canvas.translate_y + ')scale(' + canvas.scale + ')')
          .on("end", resolve);
      });

      //After zooming in
      p.then(() => {
        //Prepare the main tip for the clicked circle
        const tipContent_main = scatterPlot.genTipContent(canvas.data.topic[i], scatterPlot.pref[i]);
        const tipCoordinate_main = [canvas.width/2 + scatterPlot.tipAdjustment.x, canvas.height/2 + scatterPlot.tipAdjustment.y];
        scatterPlot.tip.main.setContent8MoveTo(tipContent_main, tipCoordinate_main);
        
        //Prepare the reference tips for the similar circles (restaurants)
        const rIds = canvas.data.closestneighbor[i];
        const tipContent_sub = rIds.map((id) => scatterPlot.genTipContent(canvas.data.topic[id], scatterPlot.pref[id]));
        const tipCoordinate_sub = rIds.map((id) => scatterPlot.getRefLocation(tx, ty, nodes[id]));
        for(const key in scatterPlot.tip) {
          let tip = scatterPlot.tip[key];
          if(tip.bindSub !== null) { tip.setContent8MoveTo(tipContent_sub[tip.bindSub], tipCoordinate_sub[tip.bindSub]); }
        }
        
        //Show all tips
        Tip.showAll();
      });
    });
}




/*
------------------------------------------------------------
Miscellaneous
------------------------------------------------------------
*/

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