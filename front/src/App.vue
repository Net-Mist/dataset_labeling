<template lang="pug">
  v-app(dark)
    v-toolbar(app absolute clipped-left)
      v-toolbar-side-icon(@click.stop="gui.nav_drawer_visible = !gui.nav_drawer_visible")
      v-toolbar-title Dataset labeling

    v-navigation-drawer(v-model="gui.nav_drawer_visible" absolute overflow app clipped)          
      //- v-toolbar(flat)
      //-   v-toolbar-side-icon(@click.stop="gui.nav_drawer_visible = !gui.nav_drawer_visible")
      //-   v-toolbar-title Options
        
      v-list        
        v-list-tile
          v-btn(color="indigo" @click="update_list_of_rectangles()") Send (s)
          v-btn(color="indigo" @click="clear_list_of_rectangles()") Clear (c)
        v-divider
        v-list-tile
          v-btn(color="indigo") Previous
        
    v-content
      v-container(grid-list-md fluid)
        v-layout(justify-space-around align-space-around)
          v-flex(xs10)
            rectangle(:href="image.src" :width="image.width" :height="image.height" drawable=true class_name="rectangles")

    v-footer(app)
      span(class="px-3") &copy; Sébastien IOOSS {{ new Date().getFullYear() }}
        
</template>

<script>
import rectangle from "./components/Rectangle";
const axios = require("axios");

export default {
  name: "App",
  components: {
    rectangle
  },
  methods: {
    update_list_of_rectangles() {
      let vm = this;
      let element = document.getElementsByClassName("rectangles");
      let polylines = element[0].getElementsByTagName("polyline");

      let points = [];
      for (let polyline of polylines) {
        points.push({
          xMin: polyline.animatedPoints[0].x,
          yMin: polyline.animatedPoints[0].y,
          xMax: polyline.animatedPoints[2].x,
          yMax: polyline.animatedPoints[2].y
        });
      }
      this.rectangles = points;

      axios
        .post("/set_image", {
          rectangles: this.rectangles,
          image_src: this.image.src
        })
        .then(function(response) {
          console.log(response);
        });

      axios.get("/get_image").then(function(response) {
        // handle success
        console.log(response);
        console.log(response["data"]);
        vm.image.src = "/" + response["data"]["image_path"];
        vm.image.width = response["data"]["width"] + "px";
        vm.image.height = response["data"]["height"] + "px";
      });

      this.clear_list_of_rectangles();
    },
    clear_list_of_rectangles() {
      let element = document.getElementsByClassName("rectangles");
      let circles = element[0].getElementsByTagName("circle");
      while (circles.length !== 0) {
        circles[0].parentNode.removeChild(circles[0]);
      }
      let polylines = element[0].getElementsByTagName("polyline");
      while (polylines.length !== 0) {
        polylines[0].parentNode.removeChild(polylines[0]);
      }

      this.rectangles = [];
    }
  },
  data() {
    return {
      gui: {
        nav_drawer_visible: true
      },
      image: {
        src: "https://picsum.photos/200/300",
        width: "200px",
        height: "300px"
      },

      rectangles: []
    };
  },
  mounted() {
    let vm = this;
    axios.get("/get_image").then(function(response) {
      // handle success
      console.log(response);
      console.log(response["data"]);
      vm.image.src = "/" + response["data"]["image_path"];
      vm.image.width = response["data"]["width"] + "px";
      vm.image.height = response["data"]["height"] + "px";
    });

    document.addEventListener(
      "keydown",
      event => {
        const keyName = event.key;
        console.log(keyName);
        if (keyName == "s") {
          vm.update_list_of_rectangles();
        }
        if (keyName == "c") {
          vm.clear_list_of_rectangles();
        }
      },
      false
    );
  }
};
</script>
