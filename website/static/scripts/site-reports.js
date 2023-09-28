function showDrop(selectRow){
    const dropIcn = selectRow.children[0].children[5].children[0];
    if(selectRow.children[1].style.maxHeight == 0){
        selectRow.children[1].style.maxHeight = "60vh";
        dropIcn.style.transform = "rotate(90deg)";
    }else{
        selectRow.children[1].style.maxHeight = null;
        dropIcn.style.transform = "rotate(360deg)";
    }
}

const tbody = document.getElementById("tbody");
const totalRow = document.getElementById("totalRow");
// add comma to စုစုပေါင်း
totalRow.children[1].children[1].innerText = parseInt(totalRow.children[1].children[1].innerText).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
totalRow.children[2].children[1].innerText = parseInt(totalRow.children[2].children[1].innerText).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
totalRow.children[3].children[1].innerText = parseInt(totalRow.children[3].children[1].innerText).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
totalRow.children[4].children[1].innerText = parseInt(totalRow.children[4].children[1].innerText).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
// add comma in table values
for(let i = 0;i < tbody.children.length; i++){
 if(tbody.children[i].children[3].innerText){
        tbody.children[i].children[3].innerText = parseInt(tbody.children[i].children[3].innerText).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
    }
    if(tbody.children[i].children[4].innerText){
        
    }
    tbody.children[i].children[5].innerText = parseInt(tbody.children[i].children[5].innerText).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});

}