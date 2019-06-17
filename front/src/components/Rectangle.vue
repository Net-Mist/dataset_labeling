<template>
  <svg :class="class_name" width="640px" height="480px">
    <image :id="image_id" :href="href" x="0" y="0" height="480px" width="640px"></image>
  </svg>
</template>

<script>
const d3 = require("d3");
export default {
  name: "points",
  props: {
    class_name: String,
    href: String, // href of the image showing in the svg
    drawable: Boolean // if true then update the points linked to drawable_name
  },
  data() {
    return {};
  },
  watch: {},
  computed: {
    image_id: function() {
      return this.class_name + "_image"
    }
  },
  mounted() {
    let vm = this; // Vue instance
    let svg = d3.select("svg." + vm.class_name);
    let g = svg.append("g");
    // document structure : svg has one group g which have many sub-group sg with one rectangle per sub-group

    let isDrawing = false;
    let newGroup = null; // when drawing a rectangle, need to remember the group of the first point we clicked
    let firstPoint = null;

    // svg.call(
    // d3.zoom().on("zoom", function() {
    // svg.attr("transform", d3.event.transform);
    // })
    // );

    svg.on("mouseup", function() {
      if (!isDrawing) {
        firstPoint = [d3.mouse(this)[0], d3.mouse(this)[1]];
        // Draw the new point
        newGroup = g.append("g");
        newGroup
          .append("circle")
          .attr("cx", firstPoint[0])
          .attr("cy", firstPoint[1])
          .attr("r", 4)
          .attr("fill", "yellow")
          .attr("stroke", "#000")
          .attr("is-handle", "true")
          .attr("cursor", "move")
          .call(d3.drag().on("drag", handleDrag));

        isDrawing = true;
      } else {
        let lastPoint = [d3.mouse(this)[0], d3.mouse(this)[1]];

        newGroup
          .append("circle")
          .attr("cx", lastPoint[0])
          .attr("cy", lastPoint[1])
          .attr("r", 4)
          .attr("fill", "yellow")
          .attr("stroke", "#000")
          .attr("is-handle", "true")
          .attr("cursor", "move")
          .call(d3.drag().on("drag", handleDrag));

        isDrawing = false;
        newGroup.select("polyline").remove();
        drawRectangle(newGroup, lastPoint, firstPoint);
      }
    });

    svg.on("mousemove", function() {
      if (!isDrawing) return;
      // let g = d3.select('g.drawPoly');
      newGroup.select("polyline").remove();
      drawRectangle(newGroup, firstPoint, [
        d3.mouse(this)[0],
        d3.mouse(this)[1]
      ]);
    });

    function drawRectangle(group, p1, p2) {
      let x_min = Math.min(p1[0], p2[0]);
      let x_max = Math.max(p1[0], p2[0]);
      let y_min = Math.min(p1[1], p2[1]);
      let y_max = Math.max(p1[1], p2[1]);

      let rectPoints = [
        [x_min, y_min],
        [x_min, y_max],
        [x_max, y_max],
        [x_max, y_min],
        [x_min, y_min]
      ];

      group
        .append("polyline")
        .attr("points", rectPoints)
        .style("fill", "none")
        .attr("stroke", "yellow");
    }

    function handleDrag() {
      // move the point
      d3.select(this)
        .attr("cx", d3.event.x)
        .attr("cy", d3.event.y);

      // find coordinates of the second point
      let circles = d3.select(this.parentNode).selectAll("circle");
      let newPoints = [];
      for (let circle of circles._groups[0]) {
        let c = d3.select(circle);
        newPoints.push([c.attr("cx"), c.attr("cy")]);
      }

      // update polyline
      d3.select(this.parentNode)
        .selectAll("polyline")
        .remove();
      drawRectangle(d3.select(this.parentNode), newPoints[0], newPoints[1]);
    }

    // be sure the image is not draggable
    document.getElementById(vm.image_id).ondragstart = function() {
      return false;
    };
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>