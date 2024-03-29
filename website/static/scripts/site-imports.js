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
        // activityTable.classList.add("d-none")
        activitiesInputs.forEach(inp => {
            console.log(inp)
            inp.removeAttribute("required")
        })
        activitiesTable.querySelectorAll("input").forEach(inp => {
            inp.value = ""
        })

        const children = Array.from(activitiesTable.children);
        console.log(children)
        const toRemove = children.slice(1, -2);

        toRemove.forEach(child => {
            activitiesTable.removeChild(child)
            console.log(child)
        });

        // activityTable.previousElementSibling.classList.add("d-none")
        notWorkingInput.style.display = "inline"
        notWorkingInput.setAttribute("required","")
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
    let blank_field = ""
    console.log("..")
    if (fstRow.previousElementSibling){
        console.log("hhd")
        const inputsInTd =  btn.parentElement.parentElement.previousElementSibling.querySelectorAll("input[required]")
        for (inp of inputsInTd){
            if (inp.value.trim() == ""){
                allowedNewRow = false
                blank_field = inp.getAttribute("data-field-name")
                break
            }
        }
    }
    console.log(blank_field)
    if (allowedNewRow){
        console.log("papi")
        let cloneRow = btn.parentElement.parentElement.nextElementSibling.cloneNode(true)
        cloneRow.querySelectorAll("input.shouldRequired").forEach(input => input.setAttribute('required', 'true'))
        cloneRow.children[0].textContent = btn.parentElement.parentElement.parentElement.children.length - 1
        cloneRow.classList.remove("d-none")
        let tableContainer =  btn.parentElement.parentElement.parentElement
        tableContainer.insertBefore(cloneRow,tableContainer.rows[tableContainer.rows.length - 2])
    }else{
        alert(` ( ${blank_field} ) အချက်အလက် မပြည့်စုံသောကြောင့် ထပ်မံ ဖြည့်သွင်း၍ မရပါ , အချက်အလက်များ ပြည့်စုံအောင် ဦးစွာ စစ်ဆေးပေးပါ !!!!!!`)
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
}