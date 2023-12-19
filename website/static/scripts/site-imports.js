function projectFill(iptCode){
            let pjCode = iptCode.value.split("|")[0].trim()
            iptCode.value = pjCode
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
            pjCode = pjCode.replace("/","thisIsSlash").trim()
            if (pjCode != ""){
                fetch(`/get-api/project-stat/${pjCode}`)
                .then(response => response.json())
                .then(result => {
                    var pjIdInp = document.getElementsByClassName("leePalKwar")[0]
                    if (result.length != 0){
                        for(let j = 0; j < labels.length; j++){
                            labels[j].style.display = "block";
                        }
                        hoAcName.innerText = `- ${result[0][1]}`;
                        prjName.innerText = `- ${result[0][2]}`;
                        prjLocation.innerText = `- ${result[0][3]}`;
                        prjDate.innerText = `- ${result[0][4]}`;
                        superVisor.innerText = `- ${result[0][5]}`;
                        pjIdInp.value = result[0][0]
                        pjIdInp.removeAttribute("required") 
                    }
                    else{
                        for(let j = 0; j < labels.length; j++){
                            labels[j].style.display = "none";
                        }
                        pjIdInp.value = ""
                        pjIdInp.setAttribute("required","")
                    }
                })
                .catch(err => console.log(err))
            }
}


function notWork(){
    const working = document.getElementById("working");
    const notWorking = document.getElementById("notWorking");
    const notWorkingInput = document.getElementById("notWorkingInput");
    const activityTable = document.getElementsByClassName("activities-table")[0]
    const activitiesTable = document.getElementById("activitiesTable")
    const activitiesInputs = activitiesTable.querySelectorAll(".notWorkInputActi")
    if(working.checked){
        notWorkingInput.style.display = "none"
        notWorkingInput.removeAttribute("required")
        activityTable.classList.remove("d-none")
        activityTable.previousElementSibling.classList.remove("d-none")
        activitiesInputs.forEach(inp => {
            inp.setAttribute("required","")
        })        
    }
    if(notWorking.checked){
        activityTable.classList.add("d-none")
        activitiesInputs.forEach(inp => {
            inp.removeAttribute("required")
        })
        activitiesTable.querySelectorAll("input").forEach(inp => {
            inp.value = ""
        })

        const children = Array.from(activitiesTable.children);
        const toRemove = children.slice(1, -2);

        toRemove.forEach(child => {
            activitiesTable.removeChild(child)
            console.log(child)
        });

        activityTable.previousElementSibling.classList.add("d-none")
        notWorkingInput.style.display = "inline"
        notWorkingInput.setAttribute("required","")
    }
}

function showUnderDisplay(btn){
    let underTable = btn.parentElement.nextElementSibling;
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
        if(parseInt(inp.value) > 23 || parseInt(inp.value) < 0){
            inp.value = 0
        }
    }else{
        inp.value = 0
    }
    addValueToTraceFuel('hourValueActivity','activitiesTable','calculatedtraceHour','traceHour')
}

function checkMin(inp){
    const regex = /^\d{0,2}$/;
    if(regex.test(inp.value)){
        if(parseInt(inp.value) > 59 || parseInt(inp.value) < 0){
        inp.value = 0
    }
    }else{
        inp.value = 0
    }
    addValueToTraceFuel('hourValueActivity','activitiesTable','calculatedtraceHour','traceHour')
}

function selection(){
    const noAff = document.getElementById("noAff");
    const affPer = document.getElementById("affPer");
    const affAll = document.getElementById("affAll");
    const wealtherAff = document.getElementById("wealtherAff");
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
        wealtherAff.value = 0
    }
    if(affPer.value != ""){
        noAff.disabled = true;
        affAll.disabled = true;
        wealtherAff.value = affPer.value
    }
    if(affAll.checked){
        noAff.disabled = true;
        affPer.disabled = true;
        wealtherAff.value = 100
    }
    if (noAff.checked || affPer.value != "" || affAll.checked){
        wealtherAff.removeAttribute("required")
    }
};

function checkInpNumber(inp,min,max){
    if (inp.value < min || inp.value > parseInt(max)){
        inp.value = 0
    }else{
        let result = 0
        let className = inp.classList[0]
        document.getElementById("manpowerTable").querySelectorAll(`.${className}`).forEach(inp => {
            result += parseInt(inp.value) || 0
        })
        document.getElementById(className).textContent = result
    }
}


function newRow(btn){
    let fstRow = btn.parentElement.parentElement
    let allowedNewRow = true
    console.log("..")
    if (fstRow.previousElementSibling){
        console.log("hhd")
        const inputsInTd =  btn.parentElement.parentElement.previousElementSibling.querySelectorAll("input[required]")
        for (inp of inputsInTd){
            if (inp.value.trim() == ""){
                allowedNewRow = false
            }
        }
    }
    if (allowedNewRow){
        console.log("papi")
        let cloneRow = btn.parentElement.parentElement.nextElementSibling.cloneNode(true)
        cloneRow.querySelectorAll("input.shouldRequired").forEach(input => input.setAttribute('required', 'true'))
        cloneRow.children[0].textContent = btn.parentElement.parentElement.parentElement.children.length - 1
        cloneRow.classList.remove("d-none")
        let tableContainer =  btn.parentElement.parentElement.parentElement
        tableContainer.insertBefore(cloneRow,tableContainer.rows[tableContainer.rows.length - 2])
    }

}

function deleteRow(trashIcon){
    if (trashIcon.parentElement.parentElement.parentElement.children.length > 3 ){
        trashIcon.parentElement.parentElement.remove();
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

<<<<<<< HEAD
function addValueToCheckBox(checkBox){
    checkBox.nextElementSibling.value = 0
    if (checkBox.checked){
        checkBox.nextElementSibling.value = 1
    }
}

function calculateInlineValue(inp){
    let targetVal = parseFloat(inp.parentElement.previousElementSibling.previousElementSibling.textContent)
    let prevVal = parseFloat(inp.parentElement.previousElementSibling.textContent)
    let curVal = parseFloat(inp.value)
    let balance = targetVal - ( prevVal  + curVal )
    console.log(balance)
    if (balance < 0.0){
        inp.value = ''
    }else{
        inp.parentElement.nextElementSibling.textContent = balance
    }
}

function calculateDiffValue(idd){
    let datas = document.querySelectorAll(`.${idd}`)
    console.log(datas)
}

function calculateInlineValueFromOther(inp,idd){
    const formValues = inp.parentElement.parentElement.getElementsByClassName(idd)
    let finalValue = parseFloat(formValues[0].textContent) - ( parseFloat(formValues[1].textContent) + parseFloat(inp.value) )
    formValues[3].textContent = parseFloat(inp.value).toFixed(2)
    formValues[4].textContent = finalValue.toFixed(2)
}

function addValueToTraceFuel(cls,parentIdd,targetCls,classNameForReplacer){
    const allFuelValues = document.getElementById(parentIdd).getElementsByClassName(cls)
    let count = 0
    let resultValue = 0.0
    if (cls == 'hourValueActivity'){
        while (count < (allFuelValues.length)-1){
            let hour = allFuelValues[count].children[0].value || 0
            let min = allFuelValues[count].children[1].value || 0
            resultValue += parseInt(hour) + (parseInt(min) / 60)
            count += 1
        }       
    }else{
        while (count < (allFuelValues.length)-1){
            resultValue += parseFloat(allFuelValues[count].value)
            count += 1
        }
    }
    document.getElementsByClassName(targetCls)[0].value = resultValue
    calculateInlineValueFromOther(document.getElementsByClassName(targetCls)[0],classNameForReplacer)
=======
function addInput(addBtn){
    const getTbody = addBtn.parentElement.parentElement.parentElement;
    if(addBtn.classList.contains("addMachine")){
        const inputTr = document.createElement("tr");
        inputTr.classList.add("stick");
        if(addBtn.parentElement.classList.contains("men-power")){
            addBtn.parentElement.innerHTML = `<button class="btn btn-md btn-danger text-white" type="button" onclick="discardInp(this)">Discard<i class="fa-solid fa-xmark ms-2"></i></button>`
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
                                        <input type="text" class="form-control w-50" placeholder="Enter Machine Name" list="machinelistOptions">
                                        <button type="button" class="btn btn-dark px-5 text-white" onclick="saveMachine(this)">Save</button>
                                    </div>
                                </td>
                                `;
            getTbody.insertBefore(inputTr , getTbody.lastElementChild);
        }
    }
    if(addBtn.classList.contains("searchMachine")){
        const inputTr = document.createElement("tr");
        inputTr.classList.add("stick");
        addBtn.parentElement.innerHTML = `<button class="btn btn-md btn-danger text-white" type="button" onclick="discardInp(this)">Discard<i class="fa-solid fa-xmark ms-2"></i></button>`
        inputTr.innerHTML = `
                                <td colspan="3" class="bg-secondary mechanicianInp">
                                    <div class="input-group px-5 z-0">
                                        <input id="searchInput" type="text" class="form-control w-50" placeholder="Search Machine Name">
                                        <button type="button" class="btn btn-dark px-5 text-white" onclick="searchMachine()">Search</button>
                                    </div>
                                </td>
                                `;
        getTbody.insertBefore(inputTr , getTbody.lastElementChild);
    }
}

// searching machine
function searchMachine(){
    const inpValue = document.getElementById("searchInput");
    const getBody = inpValue.parentElement.parentElement.parentElement.parentElement;       
        if(!inpValue.value.trim()){
            window.alert("search something baby");
        }else{           
            for(let i = 0; i < getBody.children.length - 2; i++){
                let mcName = getBody.children[i].children[0];
                console.log(mcName);
                if(mcName.parentElement.classList.contains = "d-none"){
                    mcName.parentElement.classList.remove("d-none")
                };
                if(!mcName.innerText.toUpperCase().includes(inpValue.value.toUpperCase())){
                    mcName.parentElement.classList.add("d-none");
                }
            }
        }
}

function discardInp(discardBtn){
    const getTbody = discardBtn.parentElement.parentElement.parentElement;   

    getTbody.children[getTbody.children.length - 2].remove();
    for(let i = 0; i < getTbody.children.length - 1; i++){
        if(getTbody.children[i].classList.contains = "d-none"){
            getTbody.children[i].classList.remove("d-none");
        }
    } 
    discardBtn.parentElement.innerHTML = `
                                            <button class="btn btn-md btn-primary text-white addMachine"  type="button" onclick="addInput(this)">Add Machine<i class="fa-solid fa-plus ms-2"></i></button>
                                            <button class="btn btn-md btn-primary text-white searchMachine"  type="button" onclick="addInput(this)">Search<i class="fa-solid fa-magnifying-glass ms-2"></i></button>
                                        `
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
                                <td><button class="btn btn-sm btn-success me-2" data-bs-toggle="modal" data-bs-target="#transferModal" type="button">Transfer</button><button class="btn btn-sm btn-danger">Remove</button></td>    
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
                            <td><button class="btn btn-sm btn-success me-2" data-bs-toggle="modal" data-bs-target="#transferModal" type="button">Transfer</button><button class="btn btn-sm btn-danger">Remove</button></td>    
                            `
            tbody.insertBefore(newTr, inputTr);
            save.parentElement.children[0].value = "";
            save.parentElement.children[1].value = "";
        }else{
            alert("fill the machine name baby");
        }
    };
}

function editPrjStatis(editBtn){
    const prjStatis = document.querySelector("#prjStatis");
    const getInp = prjStatis.getElementsByTagName("input");
    const getBtn = prjStatis.getElementsByTagName("button");
    const discardBtn = document.getElementById("prjDiscard");
    for(let i = 0; i < getInp.length; i++){
        if(getInp[i].disabled){
            getInp[i].disabled = false;
        }
    }
    for(let x = 0; x < getBtn.length; x++){
        if(getBtn[x].disabled){
            getBtn[x].disabled = false;
        }
    }
    editBtn.classList.add("d-none");
    discardBtn.classList.remove("d-none");
}

function savePrjStatis(saveBtn){
    location.reload();
}

//daily activites edit 
function editDaily(btn){
    const getForm = document.getElementsByClassName("body-for-daily-table");
    const getDiscard = document.getElementById("discardBtn");
    const allInput = getForm[0].getElementsByTagName("input");
    for(let i=0; i < allInput.length; i++){
        allInput[i].disabled = false;
    }
    btn.classList.add("d-none");
    getDiscard.classList.remove("d-none");
}

function discard(btn){
    const getForm = document.getElementsByClassName("body-for-daily-table");
    const getEdit = document.getElementById("editBtn");
    const allInput = getForm[0].getElementsByTagName("input");
    for(let i=0; i < allInput.length; i++){
        allInput[i].disabled = true;
    }
    btn.classList.add("d-none");
    getEdit.classList.remove("d-none");
>>>>>>> master
}