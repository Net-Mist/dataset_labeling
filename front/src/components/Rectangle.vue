<template>
  <svg :class="class_name" :width="width" :height="height">
    <image :id="image_id" :href="href" x="0" y="0" :height="height" :width="width"></image>
  </svg>
</template>

<script>
const d3 = require("d3");
export default {
  name: "points",
  props: {
    class_name: String,
    href: String, // href of the image showing in the svg
    drawable: Boolean, // if true then update the points linked to drawable_name
    height: String,
    width: String
  },
  data() {
    return {
      selected_group: null // the last d3 group created or selected
    };
  },
  watch: {},
  computed: {
    image_id: function() {
      return this.class_name + "_image";
    }
  },
  methods: {
    add_point(group, x, y) {
      let vm = this;
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
        vm.add_rectangle(
          d3.select(this.parentNode),
          newPoints[0],
          newPoints[1]
        );
      }
      function handleClick() {
        console.log("click");
        vm.selected_group = d3.select(this.parentNode);
      }
      group
        .append("circle")
        .attr("cx", x)
        .attr("cy", y)
        .attr("r", 8)
        .attr("fill", "yellow")
        .attr("opacity", "0.3")
        .attr("stroke", "#000")
        .attr("is-handle", "true")
        .attr("cursor", "move")
        .on("mousedown", handleClick)
        .call(d3.drag().on("drag", handleDrag));
    },

    add_rectangle(group, p1, p2) {
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
    },

    load_data(data) {
      let svg = d3.select("svg." + this.class_name);
      let g = svg.select("g");

      for (let rectangle of data) {
        let newGroup = g.append("g");
        this.add_point(newGroup, rectangle["xMin"], rectangle["yMin"]);
        this.add_point(newGroup, rectangle["xMax"], rectangle["yMax"]);
        this.add_rectangle(
          newGroup,
          [rectangle["xMin"], rectangle["yMin"]],
          [rectangle["xMax"], rectangle["yMax"]]
        );
      }
    },

    clear() {
      let svg = d3.select("svg." + this.class_name);
      let g = svg.select("g");
      g.selectAll("g").remove();
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
        newGroup = g.append("g");
        firstPoint = [d3.mouse(this)[0], d3.mouse(this)[1]];
        vm.add_point(newGroup, firstPoint[0], firstPoint[1]);
        isDrawing = true;
      } else {
        let lastPoint = [d3.mouse(this)[0], d3.mouse(this)[1]];
        vm.add_point(newGroup, lastPoint[0], lastPoint[1]);
        isDrawing = false;
        newGroup.select("polyline").remove();
        vm.add_rectangle(newGroup, lastPoint, firstPoint);
        vm.selected_group = newGroup;
      }
    });

    svg.on("mousemove", function() {
      if (!isDrawing) return;
      newGroup.select("polyline").remove();
      vm.add_rectangle(newGroup, firstPoint, [
        d3.mouse(this)[0],
        d3.mouse(this)[1]
      ]);
    });

    document.addEventListener(
      "keydown",
      event => {
        const keyName = event.key;
        console.log(keyName);
        if (keyName == "Escape") {
          // Cancel drawing
          if (isDrawing) {
            isDrawing = false;
            newGroup.remove();
          } else {
            vm.selected_group.remove();
          }
        }
      },
      false
    );

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