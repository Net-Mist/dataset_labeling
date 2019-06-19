<template lang="pug">
  v-app(dark)
    v-toolbar(app absolute clipped-left)
      v-toolbar-side-icon(@click.stop="gui.nav_drawer_visible = !gui.nav_drawer_visible")
      v-toolbar-title Dataset labeling
      //- v-spacer
      v-toolbar-title(class="body-2 grey--text") team : {{gui.image_id}} / {{gui.n_images}}, user : {{n_images_done_by_user}}


    v-navigation-drawer(v-model="gui.nav_drawer_visible" absolute overflow app clipped)
      v-list        
        v-list-tile
          v-tooltip(bottom)
            template(v-slot:activator="{ on }")
              v-btn(color="indigo" @click="send()" v-on="on") Send (s)
            span Press s instead of clicking here
        v-list-tile
          v-tooltip(bottom)
            template(v-slot:activator="{ on }")
              v-btn(color="indigo" @click="clear_list_of_rectangles()" v-on="on") Clear (c)
            span Press c instead of clicking here
          
        v-list-tile
          v-btn(color="indigo" :disabled="!previous_image.src" v-if="!work_on_previous" @click="go_to_previous_image()") Previous (a)
          v-btn(color="indigo" v-if="work_on_previous" @click="go_to_next_image()") Next (n)
        v-divider
        
    v-content
      v-alert(:value="true" type="info" dismissible) Press Escape to remove the last active shape
      v-container(grid-list-md fluid)
        v-layout(justify-space-around align-space-around)
          v-flex(xs10)
            rectangle(:href="image.src" :width="image.width" :height="image.height" drawable=true class_name="rectangles" ref="drawing_area")

    v-footer(app)
      span(class="px-3") &copy; Sébastien IOOSS {{ new Date().getFullYear() }}
        
</template>

<script>
import rectangle from "./components/Rectangle";
const axios = require("axios");
const d3 = require("d3");

export default {
  name: "App",
  components: {
    rectangle
  },
  methods: {
    send() {
      let vm = this;
      vm.update_list_of_rectangles();
      axios
        .post("/set_image", {
          rectangles: this.rectangles,
          image_src: this.image.src
        })
        .then(function(response) {
          console.log(response);
        });

      if (!this.work_on_previous) {
        // save data in previous image
        this.previous_image.rectangles = this.rectangles;
        this.previous_image.src = this.image.src;
        this.clear_list_of_rectangles();
        this.get_image_caller();
        this.n_images_done_by_user++;
      } else {
        this.work_on_previous = false;
        this.go_to_next_image();
      }
    },

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
    },

    get_image_caller() {
      let vm = this;
      axios.get("/get_image").then(function(response) {
        // handle success
        vm.image.src = "/" + response["data"]["image_path"];
        vm.image.width = response["data"]["width"] + "px";
        vm.image.height = response["data"]["height"] + "px";
        vm.gui.image_id = response["data"]["image_id"];
        vm.gui.n_images = response["data"]["n_images"];

        // parse data
        if (response["data"]["data"] !== {}) {
          console.log(response["data"]["data"]);
          vm.$refs.drawing_area.load_data(
            response["data"]["data"]["rectangles"]
          );
        }
      });
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
    },

    go_to_previous_image() {
      this.update_list_of_rectangles();
      // save in next image
      this.next_image.rectangles = this.rectangles;
      this.next_image.src = this.image.src;

      // load data of previous image
      this.image.src = this.previous_image.src;
      this.rectangles = this.previous_image.rectangles;

      // draw the rectangles of the previous image
      this.$refs.drawing_area.clear();
      this.$refs.drawing_area.load_data(this.rectangles);
      this.work_on_previous = true;
    },
    go_to_next_image() {
      this.update_list_of_rectangles();
      // save in previous image
      this.previous_image.rectangles = this.rectangles;
      this.previous_image.src = this.image.src;

      // load data of next image
      this.image.src = this.next_image.src;
      this.rectangles = this.next_image.rectangles;

      // draw the rectangles of the previous image
      this.$refs.drawing_area.clear();
      this.$refs.drawing_area.load_data(this.rectangles);
      this.work_on_previous = false;
    }
  },
  data() {
    return {
      gui: {
        nav_drawer_visible: true,
        image_id: 0,
        n_images: 0
      },
      image: {
        src: "https://picsum.photos/200/300",
        width: "200px",
        height: "300px"
      },
      previous_image: {
        rectangles: [],
        src: null
      },
      // only usefull when go to previous
      next_image: {
        rectangles: [],
        src: []
      },
      work_on_previous: false,

      rectangles: [],
      n_images_done_by_user: 0
    };
  },
  mounted() {
    let vm = this;
    vm.get_image_caller();

    document.addEventListener(
      "keydown",
      event => {
        const keyName = event.key;
        console.log(keyName);
        if (keyName == "s") {
          vm.send();
        }
        if (keyName == "c") {
          vm.clear_list_of_rectangles();
        }
        if (keyName == "a") {
          vm.go_to_previous_image();
        }
        if (keyName == "n") {
          vm.go_to_next_image();
        }
      },
      false
    );
  }
};
</script>
