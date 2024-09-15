
//tepig, snivy, oshawott
var pokemonArray = ["/static/images/snivy_1.png", "/static/images/tepig_1.png", "/static/images/oshawott_1.png"];
//starts with snivy 
var currIndex = 0;

function turnRight() {
    //console.log(currIndex)
    currIndex += 1;
    document.getElementById("left").src = pokemonArray[(currIndex) % pokemonArray.length]
    document.getElementById("center").src = pokemonArray[(currIndex +1) % pokemonArray.length]
    document.getElementById("right").src = pokemonArray[(currIndex +2) % pokemonArray.length]
}

function turnLeft() {
    //negative index, cant use array wrap around like turning right
    currIndex = (currIndex - 1 + pokemonArray.length) % pokemonArray.length;
    document.getElementById("left").src = pokemonArray[currIndex % pokemonArray.length];
    document.getElementById("center").src = pokemonArray[(currIndex + 1) % pokemonArray.length];
    document.getElementById("right").src = pokemonArray[(currIndex + 2) % pokemonArray.length];
}
