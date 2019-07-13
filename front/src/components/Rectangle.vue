<template>
  <svg :id="id" :width="width" :height="height">
    <image :id="imageId" :href="href" x="0" y="0" :height="height" :width="width" />
  </svg>
</template>

<script>
const d3 = require("d3");
export default {
  name: "points",
  props: {
    // SVG parameters
    id: String, // Should be unique in the whole document
    height: String,
    width: String,

    // Image parameters
    href: String, // href of the image showing in the svg

    // Drawing parameters
    selectedClassName: String, // name of the detected object
    classNamesList: Array,
    drawable: Boolean, // if true then update the points linked to drawable_name
    radius: Number
  },
  data() {
    return {
      selectedGroup: null, // the last d3 group created or selected
      colorMap: ["#ff0000", "#00e9ff", "#1aff00", "#0018ff", "#ff8a00"], // the color of the classes
      minHeight: 0,
      minWidth: 0
    };
  },
  watch: {},
  computed: {
    imageId: function() {
      return this.id + "_image";
    },
    color: function() {
      let id = this.classNamesList.findIndex(x => x == this.selectedClassName);
      return this.colorMap[id];
    }
  },
  methods: {
    /** return a list of dict containing the class and the 4 coordinates of the rectangle */
    detectedObjects() {
      let groups = d3
        .select("#" + this.id)
        .select("g")
        .selectAll("g");
      let detectedObj = [];
      groups.each(function(d) {
        let selection = d3.select(this);
        let points = selection
          .select("polyline")
          .attr("points")
          .split(",");

        detectedObj.push({
          class: String(selection.attr("class")),
          xMin: parseInt(points[0]),
          yMin: parseInt(points[1]),
          xMax: parseInt(points[4]),
          yMax: parseInt(points[5])
        });
      });
      return detectedObj;
    },
    addPoint(group, x, y) {
      let vm = this;
      function handleDrag() {
        // move the point
        d3.select(this)
          .attr("cx", d3.event.x)
          .attr("cy", d3.event.y);

        // find coordinates of the 2 points to draw the polyline
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
        vm.addRectangle(d3.select(this.parentNode), newPoints[0], newPoints[1]);
      }
      function handleClick() {
        vm.selectedGroup = d3.select(this.parentNode);
      }
      group
        .append("circle")
        .attr("cx", x)
        .attr("cy", y)
        .attr("r", vm.radius)
        .attr("opacity", "0.3")
        .attr("stroke", "#000")
        .attr("is-handle", "true")
        .attr("cursor", "move")
        .on("mousedown", handleClick)
        .call(d3.drag().on("drag", handleDrag));
    },

    addRectangle(group, p1, p2) {
      let xMin = Math.min(p1[0], p2[0]);
      let xMax = Math.max(p1[0], p2[0]);
      let yMin = Math.min(p1[1], p2[1]);
      let yMax = Math.max(p1[1], p2[1]);

      let rectPoints = [
        [xMin, yMin],
        [xMin, yMax],
        [xMax, yMax],
        [xMax, yMin],
        [xMin, yMin]
      ];

      console.log(yMax - yMin)
      console.log(xMax - xMin)
      console.log(this.minHeight)
      console.log(this.minWidth)
      if (yMax - yMin < this.minHeight || xMax - xMin < this.minWidth) {
        let color = "#ff0000";
        group
          .insert("polyline", ":first-child")
          .attr("points", rectPoints)
          .attr("stroke", color)
          .style("fill", "none");
      } else {
        group
          .insert("polyline", ":first-child")
          .attr("points", rectPoints)
          .style("fill", "none");
      }
    },

    loadData(data) {
      let g = d3.select("#" + this.id).select("g");

      for (let rectangle of data) {
        let newGroup = g
          .append("g")
          .attr("class", rectangle["class"])
          .attr(
            "stroke",
            this.colorMap[
              this.classNamesList.findIndex(x => x == rectangle["class"])
            ]
          )
          .attr(
            "fill",
            this.colorMap[
              this.classNamesList.findIndex(x => x == rectangle["class"])
            ]
          );
        this.addPoint(newGroup, rectangle["xMin"], rectangle["yMin"]);
        this.addPoint(newGroup, rectangle["xMax"], rectangle["yMax"]);
        this.addRectangle(
          newGroup,
          [rectangle["xMin"], rectangle["yMin"]],
          [rectangle["xMax"], rectangle["yMax"]]
        );
      }
    },

    clear() {
      let svg = d3.select("#" + this.id);
      let g = svg.select("g");
      g.selectAll("g").remove();
    }
  },
  mounted() {
    let vm = this; // Vue instance
    let svg = d3.select("#" + vm.id);
    let g = svg.append("g");
    // document structure : svg has one group g which have many sub-group sg with one rectangle per sub-group

    let isDrawing = false;
    let newGroup = null; // when drawing a rectangle, need to remember the group of the first point we clicked
    let firstPoint = null;

    // TODO implement zoom
    // svg.call(
    // d3.zoom().on("zoom", function() {
    // svg.attr("transform", d3.event.transform);
    // })
    // );

    svg.on("mousedown", function() {
      if (!isDrawing) {
        newGroup = g
          .append("g")
          .attr("class", vm.selectedClassName)
          .attr("stroke", vm.color)
          .attr("fill", vm.color);
        firstPoint = [d3.mouse(this)[0], d3.mouse(this)[1]];
        vm.addPoint(newGroup, firstPoint[0], firstPoint[1]);
        isDrawing = true;
      } else {
        let lastPoint = [d3.mouse(this)[0], d3.mouse(this)[1]];
        vm.addPoint(newGroup, lastPoint[0], lastPoint[1]);
        isDrawing = false;
        newGroup.select("polyline").remove();
        vm.addRectangle(newGroup, lastPoint, firstPoint);
        vm.selectedGroup = newGroup;
      }
    });

    svg.on("mousemove", function() {
      if (!isDrawing) return;
      newGroup.select("polyline").remove();
      vm.addRectangle(newGroup, firstPoint, [
        d3.mouse(this)[0],
        d3.mouse(this)[1]
      ]);
    });

    document.addEventListener(
      "keydown",
      event => {
        const keyName = event.key;
        if (keyName == "Escape") {
          // Cancel drawing
          if (isDrawing) {
            isDrawing = false;
            newGroup.remove();
          } else {
            vm.selectedGroup.remove();
          }
        }
      },
      false
    );

    // be sure the image is not draggable
    document.getElementById(vm.imageId).ondragstart = function() {
      return false;
    };
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>