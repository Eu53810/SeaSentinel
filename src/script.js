const uplTxt = document.getElementById("uplTxt")
const input = document.getElementById("imgIn")

let oceans = [["pesce pagliaccio", "delfino", "medusa", "orca", "pesce scorpione", "nautilus", "nudibranco", "polpo", "lontra", "razza", "foca", "squalo", "tartaruga marina", "balena"],
["granchio", "delfino", "anguilla", "medusa", "orca", "aragosta", "nudibranco", "polpo", "pesce palla", "anemone", "razza", "riccio di mare", "cavalluccio marino", "squalo", "gambero", "seppia", "stella marina", "tartaruga marina", "balena"],
["granchio", "delfino", "medusa", "orca", "pesce scorpione", "nautilus", "nudibranco", "polpo", "razza", "squalo", "tartaruga marina", "balena"],
["medusa", "orca", "nudibranco", "polpo", "pinguino", "razza", "foca", "squalo", "balena"],
["medusa", "orca", "nudibranco", "polpo", "razza", "foca", "squalo", "balena"],
["granchio", "delfino", "anguilla", "medusa", "orca", "aragosta", "nudibranco", "polpo", "pesce palla", "anemone", "razza", "riccio di mare", "cavalluccio marino", "squalo", "gambero", "seppia", "stella marina", "tartaruga marina", "balena"]]

uplTxt.addEventListener("click" , () => {
    input.click()
})

let fish = ""

input.addEventListener("change", (event) => {
    let file = event.target.files[0]

    if (file) {
        const reader = new FileReader()
        reader.readAsDataURL(file)

        reader.onload = (e) => {
            let img = new Image()
            img.src = e.target.result

            img.onload = async () => {
                let box = document.getElementById("imgCnvBox")
                let cnv = document.getElementById("imgCnv")
                let ctx = cnv.getContext("2d")

                cnv.width = 224; cnv.height = 224;

                ctx.drawImage(img, 0, 0, 224, 224)

                let pixels = ctx.getImageData(0, 0, 224, 224).data

                box.style.display = "block"
                document.getElementById("uplW").style.display = "none"

                cnv.width = box.clientWidth; cnv.height = box.clientHeight
                ctx.drawImage(img, 0, 0, cnv.width, cnv.height)

                let imgArr = []
                for (let i = 0; i < 224; i++) {
                    let temp1 = []
                    for (let j = 0; j < 224; j++) {
                        let tempArr = []
                        for (let k = 0; k < 3; k++) {
                            tempArr[k] = (pixels[(i*224+j)*4+k]/255)
                        }
                        temp1[j] = tempArr
                    }
                    imgArr[i] = temp1
                }

                try {
                    let response = await pywebview.api.classifyImg(imgArr);
                    document.getElementById("outBox").innerHTML = response;
                    fish = response.match(/([\w\s]+) al ([\d.,]+)%/)[1]
                } catch (error) {
                    console.error("Error classifying image:", error);
                    document.getElementById("outBox").innerHTML = "Error classifying image." + error;
                }
            }
        }
    }

    console.log(file, path)
})

document.getElementById("canc").addEventListener("click", () => {
    document.getElementById("imgCnvBox").style.display = "none"
    document.getElementById("uplW").style.display = "grid"
    document.getElementById("outBox").innerHTML = "..."
})

let mapCnv = document.getElementById("mapCnv")
let mapCtx = mapCnv.getContext("2d")

mapCnv.width = mapCnv.clientWidth; mapCnv.height = mapCnv.clientHeight

let mappetta = new Image()
mappetta.src = "./img/mappetta.jpg"

mappetta.onload = () => {
    mapCtx.drawImage(mappetta, 0, 0, mapCnv.width, mapCnv.height)
}

let hover = false

mapCnv.addEventListener("mouseenter", () => {
    hover = true
})
mapCnv.addEventListener("mouseleave", () => {
    hover = false
})

let centers = [{x: 0, y: .5, ocean: 0}, {x: 1, y: .6, ocean: 0}, {x: .35, y: .5, ocean: 1}, {x: .65, y: .6, ocean: 2}, {x: .5, y: 1, ocean: 3}, {x: .5, y: 0, ocean: 4}, {x: .55, y: .35, ocean: 5}]

window.addEventListener("mousemove", (e) => {
    if (hover) {
        let dx = e.clientX - mapCnv.offsetLeft, dy = e.clientY - mapCnv.offsetTop

        window.addEventListener("click", () => {
            mapCtx.drawImage(mappetta, 0, 0, mapCnv.width, mapCnv.height)

            mapCtx.fillStyle = "#a17fff"

            mapCtx.beginPath()
            mapCtx.arc(dx, dy, 5, 0, 2*Math.PI)
            mapCtx.fill()

            let minD = Infinity, ocean
            for(let i = 0; i < centers.length; i++) {
                let d = Math.hypot(dx - centers[i].x*mapCnv.width, dy - centers[i].y*mapCnv.height)
                if (d < minD) {
                    minD = d; 
                    ocean = centers[i].ocean
                }
            }
            document.getElementById("mapLabel").innerHTML = oceans[ocean].includes(fish, 0) ? "Specie Endemica" : "Specie Aliena"
        })
    }
})

window.addEventListener("resize", () => {
    mapCnv.width = mapCnv.clientWidth; mapCnv.height = mapCnv.clientHeight
    
    mapCtx.drawImage(mappetta, 0, 0, mapCnv.width, mapCnv.height)
})