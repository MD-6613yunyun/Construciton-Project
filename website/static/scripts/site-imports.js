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

function addInput(addBtn){
    const getTbody = addBtn.parentElement.parentElement.parentElement;
    const inputTr = document.createElement("tr");
    if(addBtn.parentElement.classList.contains("men-power")){
        addBtn.parentElement.innerHTML = `<button class="btn btn-md btn-danger text-white"  type="button" onclick="discardInp(this)">Discard<i class="fa-solid fa-xmark ms-2"></i></button>`
        inputTr.innerHTML = `
                            <td colspan="3" class="bg-secondary mechanicianInp">
                                <div class="input-group px-5 z-0">
                                    <input type="text" class="form-control w-50" placeholder="Enter Machine Name" list="machinelistOptions">
                                    <input type="number" class="form-control" placeholder="Enter Mans Power">
                                    <button type="button" class="btn btn-dark px-5 text-white" onclick="saveMachine(this)">Save</button>
                                </div>
                            </td>
                            `;
        getTbody.insertBefore(inputTr , getTbody.lastElementChild);
    }else{
        addBtn.parentElement.innerHTML = `<button class="btn btn-md btn-danger text-white"  type="button" onclick="discardInp(this)">Discard<i class="fa-solid fa-xmark ms-2"></i></button>`
        inputTr.innerHTML = `
                            <td colspan="3" class="bg-secondary meName">
                                <div class="input-group px-5 z-0">
                                    <input type="text" class="form-control w-50" data-bs-toggle="dropdown" placeholder="Enter Machine Name" list="machinelistOptions">
                                    <button type="button" class="btn btn-dark px-5 text-white" onclick="saveMachine(this)">Save</button>
                                </div>
                            </td>
                            `;
        getTbody.insertBefore(inputTr , getTbody.lastElementChild);
    }
}

function discardInp(discardBtn){
    const getTbody = discardBtn.parentElement.parentElement.parentElement;
    getTbody.children[getTbody.children.length - 2].remove();
    discardBtn.parentElement.innerHTML = `<button class="btn btn-md btn-primary text-white"  type="button" onclick="addInput(this)">Add Machine<i class="fa-solid fa-plus ms-2"></i></button>`
}

function saveMachine(save){
    const tbody = save.parentElement.parentElement.parentElement.parentElement;
    const inputTr = save.parentElement.parentElement.parentElement;
    const machineName = save.parentElement.children[0].value;
    const manPower = save.parentElement.children[1].value;
    if(inputTr.children[0].classList.contains("mechanicianInp")){
        if(!machineName == "" && manPower > 0){
                const newTr = document.createElement("tr");
                newTr.className = "text-center fs-6";
                newTr.innerHTML = `
                                <td>${machineName}</td>
                                <td>${manPower}</td>
                                <td><button class="btn btn-sm btn-success me-2">Transfer</button><button class="btn btn-sm btn-danger">Remove</button></td>    
                                `
                tbody.insertBefore(newTr, inputTr);
                save.parentElement.children[0].value = "";
                save.parentElement.children[1].value = "";
            }else{
                alert("fill the machine name baby");
            }
    }else if(inputTr.children[0].classList.contains("meName")){
        if(!machineName == ""){
            const newTr = document.createElement("tr");
            newTr.className = "text-center fs-6";
            newTr.innerHTML = `
                            <td>${machineName}</td>
                            <td>Budozer</td>
                            <td><button class="btn btn-sm btn-success me-2">Transfer</button><button class="btn btn-sm btn-danger">Remove</button></td>    
                            `
            tbody.insertBefore(newTr, inputTr);
            save.parentElement.children[0].value = "";
            save.parentElement.children[1].value = "";
        }else{
            alert("fill the machine name baby");
        }
    };
}