<template lang="pug">
  v-app(dark)
    v-toolbar(app absolute clipped-left)
      v-toolbar-side-icon(@click.stop="gui.navDrawerVisible = !gui.navDrawerVisible")
      v-toolbar-title Dataset labeling
      //- v-spacer
      v-toolbar-title(class="body-2 grey--text") team : {{gui.nImagesDoneByTeam}} / {{gui.nImagesToDoByTeam}}, user : {{nImagesDoneByUser}}


    v-navigation-drawer(v-model="gui.navDrawerVisible" absolute overflow app clipped)
      v-list        
        v-list-tile
          v-tooltip(bottom)
            template(v-slot:activator="{ on }")
              v-btn(color="indigo" @click="send()" v-on="on") Send (s)
            span Press s instead of clicking here
        v-list-tile
          v-tooltip(bottom)
            template(v-slot:activator="{ on }")
              v-btn(color="indigo" @click="$refs.drawingArea.clear()" v-on="on") Clear (c)
            span Press c instead of clicking here
          
        v-list-tile
          v-btn(color="indigo" :disabled="!previousImage.src" v-if="!workOnPrevious" @click="goToPreviousImage()") Previous (a)
          v-btn(color="indigo" v-if="workOnPrevious" @click="goToNextImage()") Next (n)
        v-divider

        v-list-tile
          v-flex(xs12)
            v-slider(v-model="gui.radius" label="Radius" thumb-label min=6 max=20)

        v-list-tile
          v-flex(xs12)
            v-select(:items="classNames" label="Class" v-model="selectedClassName")
        
    v-content
      //- v-alert(:value="true" type="info" dismissible) If you want to edit you last image, press a, edit the image and press s to re-send data {{selectedClassName}}
      v-container(grid-list-md fluid)
        v-layout(justify-space-around align-space-around)
          v-flex(xs10)
            rectangle(:href="image.src" :width="image.width" :height="image.height" 
                      drawable=true id="rectangles" 
                      :selectedClassName="selectedClassName" :radius="gui.radius"
                      :classNamesList="classNames" ref="drawingArea")

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
      let detectedObjects = vm.$refs.drawingArea.detectedObjects();
      console.log(detectedObjects);
      axios
        .post(vm.serverUrl + "/set_image", {
          detectedObjects: detectedObjects,
          imageSrc: this.image.src
        })
        .then(function(response) {
          if (!vm.workOnPrevious) {
            // save data in previous image
            vm.previousImage.detectedObjects = detectedObjects;
            vm.previousImage.src = vm.image.src;
            vm.$refs.drawingArea.clear();
            vm.getImage();
            vm.nImagesDoneByUser++;
          } else {
            vm.workOnPrevious = false;
            vm.goToNextImage();
          }
        });
    },

    getImage() {
      let vm = this;
      axios.get(vm.serverUrl + "/get_image").then(function(response) {
        // handle success
        vm.image.src = vm.imageUrl + "/" + response["data"]["image_path"];
        vm.image.width = response["data"]["width"] + "px";
        vm.image.height = response["data"]["height"] + "px";
        vm.gui.nImagesDoneByTeam = response["data"]["image_id"];
        vm.gui.nImagesToDoByTeam = response["data"]["n_images"];

        // parse data
        if ("rectangles" in response["data"]["data"]) {
          vm.$refs.drawingArea.loadData(response["data"]["data"]["rectangles"]);
        }
      });
    },

    getClassNames() {
      let vm = this;
      axios.get(vm.serverUrl + "/get_classes").then(function(response) {
        vm.classNames = response["data"]["classNames"];
        console.log(vm.classNames)
        if (vm.classNames.length > 0) {
          vm.selectedClassName = vm.classNames[0];
        }
        console.log(response["data"])
        let classColors = response["data"]["classColors"];
        console.log(classColors)

        if (classColors.length == vm.classNames.length)
          vm.$refs.drawingArea.colorMap = classColors;
      });
    },
    goToPreviousImage() {
      // save in next image
      console.log("save current image in next image");
      console.log(this.$refs.drawingArea.detectedObjects());
      this.nextImage.detectedObjects = this.$refs.drawingArea.detectedObjects();
      console.log(this.nextImage.detectedObjects);
      this.nextImage.src = this.image.src;

      // load data of previous image
      this.image.src = this.previousImage.src;
      this.$refs.drawingArea.clear();
      this.$refs.drawingArea.loadData(this.previousImage.detectedObjects);
      this.workOnPrevious = true;
    },
    goToNextImage() {
      // save in previous image
      this.previousImage.detectedObjects = this.$refs.drawingArea.detectedObjects();
      this.previousImage.src = this.image.src;

      // load data of next image
      this.image.src = this.nextImage.src;
      this.$refs.drawingArea.clear();
      this.$refs.drawingArea.loadData(this.nextImage.detectedObjects);
      this.workOnPrevious = false;
    }
  },
  data() {
    return {
      gui: {
        navDrawerVisible: true, // control if the lateral menu is visible
        nImagesDoneByTeam: 0, // updated each time we get a new image from python server
        nImagesToDoByTeam: 0, // updated each time we get a new image from python server
        radius: 6 // radius of the circles to draw
      },
      image: {
        src: "https://picsum.photos/200/300", // path of the image
        width: "200px", // value send by the python server at the same time than the image
        height: "300px" // value send by the python server at the same time than the image
      },
      previousImage: {
        detectedObjects: [],
        src: null
      },
      // only useful when go to previous
      nextImage: {
        detectedObjects: [],
        src: null
      },
      workOnPrevious: false,
      nImagesDoneByUser: 0,
      // serverUrl: "http://127.0.0.1:5000",
      // imageUrl: "http://127.0.0.1:5000",
      serverUrl: "",
      imageUrl: "",
      classNames: [],
      selectedClassName: ""
    };
  },
  mounted() {
    let vm = this;
    vm.getImage();
    vm.getClassNames();

    document.addEventListener(
      "keydown",
      event => {
        const keyName = event.key;
        console.log(keyName)
        if (keyName == "s") {
          vm.send();
        }
        if (keyName == "c") {
          vm.$refs.drawingArea.clear();
        }
        if (keyName == "a") {
          vm.goToPreviousImage();
        }
        if (keyName == "n") {
          vm.goToNextImage();
        }
        if (keyName == "x" || keyName == "Tab") {
          let id = vm.classNames.findIndex(x => x == vm.selectedClassName);
          id++;
          if (id >= vm.classNames.length) id = 0;
          vm.selectedClassName = vm.classNames[id];
        }
      },
      false
    );
  }
};
</script>
