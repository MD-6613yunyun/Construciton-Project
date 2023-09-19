const data = [
    {
        projectCode : "MDMM-0010",
        hoName : "Theint Theint San",
        projectName : " AYA-Pathein-Gway To-Byait Kone Chaung",
        projectLocation : "Ayawady",
        projectStartDate : "18/12/2021",
        supervisor : "Myoe Min Naung@Tote Gyi"
    },{
        projectCode : "MDMM-0020",
        hoName : "Mar Mar Win",
        projectName : " AYA-Yangon-Gway To-Chaung Thar",
        projectLocation : "Myaynigone",
        projectStartDate : "18/12/2021",
        supervisor : "Aung Min Thein@Phote Gyi"
    },{
        projectCode : "MDMM-0030",
        hoName : "Kyaw Kyaw",
        projectName : "Shwe-Pyi-Thar To-Hlel-Guu",
        projectLocation : "Brooklyn",
        projectStartDate : "18/12/2021",
        supervisor : "Kway Chung Kyi@Ta Yote Gyi"
    },{
        projectCode : "MDMM-0040",
        hoName : "Theint Theint San",
        projectName : " AYA-Pathein-Gway To-Byait Kone Chaung",
        projectLocation : "Ayawady",
        projectStartDate : "18/12/2021",
        supervisor : "Myoe Min Naung@Tote Gyi"
    },{
        projectCode : "MDMM-0050",
        hoName : "Mar Mar Win",
        projectName : " AYA-Yangon-Gway To-Chaung Thar",
        projectLocation : "Myaynigone",
        projectStartDate : "18/12/2021",
        supervisor : "Aung Min Thein@Phote Gyi"
    },{
        projectCode : "MDMM-0060",
        hoName : "Kyaw Kyaw",
        projectName : "Shwe-Pyi-Thar To-Hlel-Guu",
        projectLocation : "Brooklyn",
        projectStartDate : "18/12/2021",
        supervisor : "Kway Chung Kyi@Ta Yote Gyi"
    }
]

function projectFill(iptCode){
            const hoAcName = document.getElementById("hoAcName");
            const prjName = document.getElementById("prjName");
            const prjLocation = document.getElementById("prjLoca");
            const prjDate = document.getElementById("prjDate");
            const superVisor = document.getElementById("sprVisor");
            const labels = document.getElementsByClassName("label");
            hoAcName.innerText = ``;
            prjName.innerText = ``;
            prjLocation.innerText = ``;
            prjDate.innerText = ``;
            superVisor.innerText = ``;
            for(let j = 0; j < labels.length; j++){
                labels[j].style.display = "block";
            }
            for(let i = 0; i < data.length ; i++){
                if(iptCode.value === data[i].projectCode){
                    hoAcName.innerText = `- ${data[i].hoName}`;
                    prjName.innerText = `- ${data[i].projectName}`;
                    prjLocation.innerText = `- ${data[i].projectLocation}`;
                    prjDate.innerText = `- ${data[i].projectStartDate}`;
                    superVisor.innerText = `- ${data[i].supervisor}`;
                }
            }
}


function notWork(){
    const working = document.getElementById("working");
    const notWorking = document.getElementById("notWorking");
    const notWorkingInput = document.getElementById("notWorkingInput");
    if(working.checked){
        notWorkingInput.style.display = "none"
    }
    if(notWorking.checked){
        notWorkingInput.style.display = "inline"
    }
}

function showUnderDisplay(btn){
    let underTable = btn.parentElement.nextElementSibling
    if (underTable.classList.contains("toggle-table")){
        underTable.classList.remove("toggle-table")
        btn.classList.replace("fa-plus","fa-minus")
    }else{
        underTable.classList.add("toggle-table")
        btn.classList.replace("fa-minus","fa-plus")
    }
}

function checkHour(inp){
    const regex = /^\d{0,2}$/;
    if(regex.test(inp.value)){
        console.log(inp.value)
        if(parseInt(inp.value) > 23 || parseInt(inp.value) < 0){
        inp.value = ""
    }
    }else{
        inp.value = ""
    }
}

function checkMin(inp){
    const regex = /^\d{0,2}$/;
    if(regex.test(inp.value)){
        if(parseInt(inp.value) > 59 || parseInt(inp.value) < 0){
        inp.value = ""
    }
    }else{
        inp.value = ""
    }
}

function selection(){
    const noAff = document.getElementById("noAff");
    const affPer = document.getElementById("affPer");
    const affAll = document.getElementById("affAll");
    noAff.disabled = false;
    affPer.disabled = false;
    affAll.disabled = false;
    if(affPer.value){
        if(affPer.value > 100){
            affPer.value = "";
        };
    }
    if(noAff.checked){
        affPer.disabled = true;
        affAll.disabled = true;
    }
    if(!affPer.value == ""){
        noAff.disabled = true;
        affAll.disabled = true;
    }
    if(affAll.checked){
        noAff.disabled = true;
        affPer.disabled = true;
    }
};

function checkInpNumber(inp,min,max){
    if (inp.value < min || inp.value > max){
        inp.value = 0
    }
}


function newRow(btn){
    cloneRow = btn.parentElement.nextElementSibling.cloneNode(true)
    cloneRow.children[0].textContent = btn.parentElement.parentElement.children.length - 1
    cloneRow.classList.remove("d-none")
    let tableContainer =  btn.parentElement.parentElement
    tableContainer.insertBefore(cloneRow,tableContainer.rows[tableContainer.rows.length - 2])
}

function deleteRow(trashIcon){
    if (trashIcon.parentElement.parentElement.children.length > 3 ){
        trashIcon.parentElement.remove();
    }
}

function fillValue(tr){
    const quan = tr.getElementsByClassName("quan")[0];
    const prc = tr.getElementsByClassName("prc")[0];
    const amt = tr.getElementsByClassName("amt")[0];
    if(quan.value){
        quan.value = roundToTwoDecimalPlaces(parseFloat(quan.value));
    }
    if(prc.value){
        prc.value = roundToTwoDecimalPlaces(parseFloat(prc.value));
    }
    if(quan.value && prc.value){
        let amtVal = roundToTwoDecimalPlaces(quan.value * prc.value);
        amt.value = amtVal;
    }
    const amount = document.getElementsByClassName("amt");
    const total = document.getElementById("total")
    let sum = 0;
    for(let i = 0; i < amount.length; i++){
        if(amount[i].value != ""){
            sum += parseFloat(amount[i].value);
        }
    }
    total.textContent = sum;
}

function roundToTwoDecimalPlaces(number) {
    return Math.round(number * 100) / 100;
}