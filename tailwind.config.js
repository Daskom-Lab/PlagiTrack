module.exports = {
  content: [
      "./templates/**/*.html",
      "./static/src/**/*.js",
      "./node_modules/flowbite/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        'light-blue': '#3599C2',  
        'deep-blue': '#105B7A', 
      },
    },
  },
  plugins: [
    require("flowbite/plugin")
  ],
}