let belowing = []

function create_add_machine_input(btn,event){
    btn.style.display = 'none'
    btn.nextElementSibling.style.display = ""
    belowing = Array.from(btn.parentElement.parentElement.parentElement.parentElement.children).map(element => element);
    event.preventDefault();
}

function insert_data_and_return_back_button(btn){
    belowing = []
}

function giveProjectCodes(idd = 'aboveProjectCodes'){
    let abovePj = document.getElementById(idd)
    if (abovePj && abovePj.innerHTML.trim() == ""){
        fetch("/get-pj-datas")
        .then(response => response.json())
        .then(result => {
            abovePj.innerHTML = ""
            for (const dt of result){
                abovePj.innerHTML += `<p class="m-1 ms-2" shopID="${dt[0]}" projectCode="${dt[2]}" onclick="assignShop(this)">${dt[1]} _&_ ${dt[2]}</p>`
            }
        })
        .catch(err => console.log(err))
    }
}

function showModalAndGiveProjectCodes(opt='normal'){
    giveProjectCodes()
    if (opt == 'normal'){
        let modalContainer = document.getElementById("monthlyReport")
        modalContainer.getElementsByClassName("modal-title")[0].textContent = "Income Expense Report"
        let checkerRadio = modalContainer.getElementsByClassName("form-check-input")[0]
        checkerRadio.setAttribute("checked","")
        checkEachMachineOrAll(checkerRadio)
        checkerRadio.parentElement.classList.add("d-none")
        modalContainer.querySelector("form").setAttribute("action","/duty/income-expense-report")
    }else if (opt == 'monthly'){
        let modalContainer = document.getElementById("monthlyReport")
        modalContainer.getElementsByClassName("modal-title")[0].textContent = "Income Expense Report"
        let checkerRadio = modalContainer.getElementsByClassName("form-check-input")[0]
        checkerRadio.removeAttribute("checked")
        checkEachMachineOrAll(checkerRadio)        
    }else if (opt == 'remove-date'){
        let url_route_part = document.getElementById("chooseProjectBeforeCreateForm").classList[4]
        let modalContainer = document.getElementById("monthlyReport")
        modalContainer.getElementsByClassName("modal-title")[0].textContent = "Project Choice for Daily Activity"
        let checkerRadio = modalContainer.getElementsByClassName("form-check-input")[0]
        checkerRadio.setAttribute("checked","")
        checkEachMachineOrAll(checkerRadio)
        checkerRadio.parentElement.nextElementSibling.classList.add("d-none")
        checkerRadio.parentElement.classList.add("d-none")
        modalContainer.querySelector("form").setAttribute("action",`/site-imports/${url_route_part}/create`)        
    }
}

function checkSupervisor(){
    let modalBody = document.getElementById("inside-statistics-modal-body")
    let codeName = document.getElementById("projectCode")
    modalBody.innerHTML = ""
    if (document.getElementById("project_id_for_stat").value.trim() == ""){
        modalBody.innerHTML += `<h4>Invalid Project Name / Code : <strong class='text-danger'> ${codeName.value}</strong></h4>`        
    }
    else{
        let closeBtn = document.getElementById("inModalStatisticsClose")
        let submitBtn = document.getElementById("inModalStatistics");
        let sup = document.getElementsByClassName("site-supervisors")[0].value.trim()
        let acc = document.getElementsByClassName("hoAccount")[0].value.trim()
        fetch(`/get-api/accountant-supervisor-check/${sup}~|~${acc}`)
        .then(response => response.json())
        .then(result => {
            if (result[0] == null){
                modalBody.innerHTML += `<h4>Invalid Supervisor ${sup}</h4>`
            }else if (result[1] == null){
                modalBody.innerHTML += `<h4>Invalid HO / ACC ${acc}</h4>` 
            }else{
                document.getElementById("site-supervisors-id").value = result[0][0]
                document.getElementById("ho-account-id").value = result[1][0]
                modalBody.innerHTML += "You are seeing this form becuase you haven't input required data.."
                submitBtn.click()
                closeBtn.click()
            }
        })
    }
}

function callProjectStatistics(btn){
    btn.parentElement.previousElementSibling.previousElementSibling.textContent += ` of ${btn.textContent}`
    btn.parentElement.previousElementSibling.value = btn.textContent
    btn.parentElement.style.display = 'none'
    let statTable = document.getElementById("table-stat")
    let pjIdd = btn.getAttribute('shopID')

    fetch(`/duty/call-project-statistics/${pjIdd}`)
    .then(response => response.json())
    .then(result => {
        if (result.length != 0){
            // console.log(result)
            statTable.style.display = ""
            tab = document.getElementById('body-data-of-stats-table')
            let fst_row = ""
            let sec_row = ""
            let temp_result = result.slice(1)
            for (let dt of temp_result){
                fst_row += `<td>${dt}</td>`
            }
            for (let idx in temp_result){
                if (idx == 0 || idx == 1){
                    sec_row += `<td><input value="${temp_result[idx]}" disabled/></td>`
                }else{
                    sec_row += `<td><input value="${temp_result[idx]}"/></td>`
                }
            }
            tab.innerHTML = `<tr>
                                <td style="cursor: pointer;" onclick='delete_project_statistics(this,${result[0]})'>🗑️</td>
                                ${fst_row}
                            </tr>
                            <tr>
                                <td style="cursor: pointer;" onclick='edit_project_statistics(this,${result[0]})'>✅</td>
                                ${sec_row}
                            </tr>`
        }
    })
    .catch(err => console.log(err))

}

function assignIDForEachLine(opt){
    console.log(opt)
}

function chooseMachineInSelect(btn){
    machine_data = btn.value.split("|")
    list = document.getElementById("machineListForProjectStats")
    if(!Array.from(document.querySelectorAll('td')).map(td => td.textContent.trim()).includes(machine_data[0].trim())){
        list.innerHTML +=  `<tr style='font-size:13px;'>
                                <td class="d-none"><input name="machine-ids" value="${machine_data[1].trim()}"></td>
                                <td class="added-machines">${machine_data[0].trim()}</td>
                                <td>
                                    <button type="button" onclick="removeTdRow(this)" class="btn btn-sm btn-danger"> Transfer / Move</button>
                                </td>
                            </tr>`
    }
    btn.value = ""
}

function removeTdRow(td){
    td.parentElement.parentElement.remove()
}

function send_dropdown_data(btn,...kwargs){
    console.log(kwargs)
    let collapser = btn.parentElement.nextElementSibling.nextElementSibling.nextElementSibling
    let dropdownHolders = collapser.getElementsByClassName('dropdown-holders')
    fetch(`/import/return-dropdown-data/${kwargs.join()}`)
    .then(response => response.json())
    .then(result => {
        for (const idx in result){
            dropdownEle = dropdownHolders[idx]
            console.log(dropdownHolders[idx])
            console.log(result[idx])
            const newDiv = document.createElement('div');

            newDiv.style.maxHeight = '150px';
            newDiv.style.overflowY = 'auto';
            newDiv.style.display = 'none';

            for (const item of result[idx]){
                console.log(item)
                newDiv.innerHTML += `<p class="m-1 ms-2" id="${item[0]}"  onclick="assignInput(this)">${item[1]}</p>`
            }
            dropdownHolders[idx].parentNode.insertBefore(newDiv, dropdownHolders[idx].nextSibling)
        }
    })
    .catch(err => console.log(err))   
}

function delete_project_statistics(btn,idd,for_stats=true,for_pj_lst=true){
    if (for_stats){
        db = 'project_statistics'
    }else if(for_pj_lst){
        db = 'analytic_project_code'
    }
    else{
        db = 'fleet_vehicle'
    }
    fetch(`/delete-data/${db}/${idd}`)
    .then(response => response.text())
    .then(result => {
        if (result == 'Success'){
            if (for_stats){
                btn.parentElement.remove()
                btn.parentElement.previousElementSibling.remove()
            }else{
                btn.parentElement.parentElement.previousElementSibling.remove()
                btn.parentElement.parentElement.remove()
            }
        }
    })
    .catch(err => console.log(err))
}

function deleteTheWholeForm(db,idd){
    fetch(`/delete-data/${db}/${idd}`)
    .then(response => response.text())
    .then(result => {
        if (result == 'Success'){
            let route_with_db = {'income_expense':'/site-imports/income-expense/view'}
            window.location = route_with_db[db]
        }else{
            window.alert(result)
        }
    })
    .catch(err => console.log(err))  
}

// clicker = document.getElementById("autoClicker")
// modalUserMgs = document.getElementById("modalUserWarn")
// if (modalUserMgs.innerHTML.trim() != "<strong>None</strong>"){
//     clicker.click()
// }



function search_and_add(inp,event){
    let filter = inp.value.toUpperCase()
    if (filter.trim() != "" && event.keyCode != 13){
        for (let i = 1; i < belowing.length; i++) {
            let txtValue = belowing[i].textContent || belowing[i].innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
            belowing[i].style.display = "";
            } else {
            belowing[i].style.display = "none";
            }
        }
    }else if (event.keyCode == 13){
        console.log("nani")
        inp.parentElement.style.display = "none"
        inp.parentElement.previousElementSibling.style.display = ""
        for (let i = 1; i < belowing.length; i++) {
            belowing[i].style.display = ""
        }
    }
}

function chngInp(btn){
    btn.parentElement.innerHTML = `<input type="text"  dbTable="${btn.getAttribute('dbTable')}" value="${btn.getAttribute('data-machine')}" idd="${btn.id}" onkeyup="updateEachMachine(this,event)"/>`
}

function updateEachMachine(inp,event){
    if (event.keyCode == 13){
        fetch(`/import/update-each-machine-details/${inp.getAttribute("dbTable")}/${inp.getAttribute("idd")}/${inp.value.trim()}`)
        .then(response => response.text() )
        .then(result => inp.parentElement.innerHTML = inp.value)
        .catch(e => console.log(e))
    }
}

offsetLimit  = 81
function clickPagination(btn,target,txt){
    target_mapp = {"pj":"pj-data-changeable",
                  "Duty Query":"duty-query-changeable",
              "machine":"machine-list-changeable",
              "Expenses Query":"expense-list-changeable"}
    all_tr = document.getElementsByClassName(target_mapp[target])
    if (txt == 'prev'){
        displayAmt = btn.nextElementSibling.textContent.trim().split("/")
        getTotal = displayAmt[1]
        last = displayAmt[0].split("-")[1]
        fst = Number(displayAmt[0].split("-")[0])
        if (fst != 1){
            fetch(`/offset-display/${target_mapp[target]}/${fst-81}`)
            .then(response => response.json())
            .then(result => {
                btn.nextElementSibling.textContent = `${fst-81}-${fst-1} / ${getTotal}`
                replaceTableData(result)
            })
            .catch(err => console.log(err))
        }
        
    }else{
        displayAmt = btn.previousElementSibling.textContent.trim().split("/")
        getTotal = Number(displayAmt[1])
        last = Number(displayAmt[0].split("-")[1])
        if (last != getTotal){
            fetch(`/offset-display/${target_mapp[target]}/${last}`)
            .then(response => response.json())
            .then(result => {
                if(last+82 > Number(getTotal)){
                    btn.previousElementSibling.textContent = `${last+1}-${getTotal} / ${getTotal}`
                }else{
                    btn.previousElementSibling.textContent = `${last+1}-${last+81} / ${getTotal}`
                }
                replaceTableData(result)
            })
            .catch(err => console.log(err))
        }
    }
}

function replaceTableData(result) {
    console.log(all_tr)
    let i = 0;
    for (i = 0; i < result.length; i++) {
      tds = all_tr[i].getElementsByTagName('td');
      Array.from(tds).forEach((td, index) => {
        td.innerText = result[i][index];
      });
    }
}  

function getShops(inp){
    dropperDiv = inp.nextElementSibling
    if (inp.value.length !== 0){
        dropperDiv.style.display = "";
    }else{
        dropperDiv.style.display = "none";
    }
    filter = inp.value.toUpperCase();
    let a = dropperDiv.getElementsByTagName("p");
    for (let i = 0; i < a.length; i++) {
        let txtValue = a[i].textContent || a[i].innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
        a[i].style.display = "";
        } else {
        a[i].style.display = "none";
        }
    }
}

function getShopsSelect(inp){
    dropperDiv = inp.nextElementSibling
    if (inp.value.length !== 0){
        dropperDiv.style.display = "";
    }else{
        dropperDiv.style.display = "none";
    }
    filter = inp.value.toUpperCase();
    let a = dropperDiv.getElementsByTagName("option");
    for (let i = 0; i < a.length; i++) {
        let txtValue = a[i].textContent || a[i].innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
        a[i].style.display = "";
        } else {
        a[i].style.display = "none";
        }
    }
}




function edit_data(trClick,for_pj_lst=false){
    let idd = trClick.id
    if ( (!trClick.nextElementSibling) || (!trClick.nextElementSibling.getAttribute('machineEachData'))){
    let tdData = document.createElement('tr')
    tdData.setAttribute('machineEachData','yes')
    tdData.innerHTML = `<td>
                            <span onclick='delete_project_statistics(this,${idd},false,${for_pj_lst})' style='cursor:pointer'>🗑️</span>
                            <span onclick='edit_project_statistics(this,${idd},false,${for_pj_lst})' style='cursor:pointer'>✔️</span>
                        </td>`
    Array.from(trClick.getElementsByTagName('td')).slice(1).forEach(ele => {
        tdData.innerHTML += `<td><input value='${ele.innerText}'/></td>`
    })
    trClick.parentNode.insertBefore(tdData,trClick.nextSibling)
    }else{
        trClick.nextElementSibling.remove()
    }
}

/* edit project data or machine data */
function edit_project_statistics(btn,idd,for_stats=true,for_pj_lst=false){
    let send_datas = ''
    let slicing_arr = '';
    if (for_stats){
        slicing_arr = Array.from(btn.parentElement.getElementsByTagName('td')).slice(3)
        db = 'project_statistics'
    }else{
        slicing_arr = Array.from(btn.parentElement.parentElement.getElementsByTagName('td')).slice(1)
        if (for_pj_lst){
            db = 'analytic_project_code'
        }else{
            db = 'fleet_vehicle'            
        }

    }
    slicing_arr.forEach(ele =>{
        send_datas += `${ele.children[0].value.replace(/\//g,'thisIsSlash')},`
    })
    console.log(send_datas.slice(0,-1))
    console.log(idd)
    fetch(`/edit-data/${db}/${idd}/${send_datas.slice(0,-1)}`)
    .then(response => response.json())
    .then(result => {
        if (result[0] == 'Error'){
            console.log('Wrong Data')
            mgsContainer = document.getElementById('modalUserWarn')
            mgsContainer.innerHTML = `Unknown Field or Unknow Value at <strong class='text-danger'> ${result[1]} </strong>`
            autoClick = document.getElementById('autoClicker')
            autoClick.click()
        }else{
            if (for_stats){
                btn.parentElement.remove()
            }else{
                btn.parentElement.parentElement.remove()
            }
            
        }
    })
    .catch(err => console.log(err))
}
function checkEachMachineOrAll(btn){
    all_children_in_div = btn.parentElement.parentElement.children
    action_of_form = btn.parentElement.parentElement.parentElement
    if (btn.checked){
        all_children_in_div[3].classList.remove('d-none')
        for (let idx of [4,5,6]){
            all_children_in_div[idx].classList.add('d-none')
        }
        action_of_form.setAttribute('action','/duty/report-by-each-machine')
    }else{
        all_children_in_div[3].classList.add('d-none')
        for (let idx of [4,5,6]){
            all_children_in_div[idx].classList.remove('d-none')
        }
        action_of_form.setAttribute('action','/duty/get-monthly-duty')
    }
}

function check_or_trace_start_date(inp){
    start_dt = inp.previousElementSibling.previousElementSibling.value.split('-')
    end_dt = inp.value.split("-")
    if (start_dt[0] != end_dt[0] || start_dt[1] != end_dt[1]){
        mgsContainer = document.getElementById('modalUserWarn')
        mgsContainer.innerHTML = `<strong class='text-danger'> Your date range exceeded our limits.. Maximum one month is valid.. </strong>`
        autoClick = document.getElementById('autoClicker')
        autoClick.click()
        inp.value = inp.previousElementSibling.previousElementSibling.value
    }
    
}


function assignShop(btn){
    let idd = btn.getAttribute('shopID')
    let pjCode = btn.getAttribute('projectCode')
    let pjEle  = document.getElementById("pjCode")
    pj_name = btn.innerText.split('_&_')[0]
    btn.parentElement.parentElement.previousElementSibling.innerText = pj_name
    btn.parentElement.parentElement.children[0].setAttribute('value',idd)
    btn.parentElement.parentElement.children[1].setAttribute('value',btn.innerText)
    pjEle.style.display = ""
    pjEle.textContent = pjCode
}

function assignInput(btn){
    btn.parentElement.previousElementSibling.value = btn.textContent
    btn.parentElement.style.display = 'none';
}



if (window.location.href.endsWith("/duty/get-monthly-duty")){
    excavators = document.getElementsByClassName("excavator")
    reportTable = document.getElementById("report-data-container")

    excavators[0].style.display = ""

    time_wrong_formats = document.getElementsByClassName("time_wrong_format")
    fuel_formats = document.getElementsByClassName("fuel_column")
    for (let time_wrong of time_wrong_formats){
        let durationText = time_wrong.innerText.trim()
        // console.log(durationText)
        if (durationText.includes(", ")){
            front = durationText.split(", ")
            days = Number(front[0].split(" ")[0])
            timee = front[1].split(":")
            result_date = `${Number(timee[0])+(days*24)}:${timee[1]}`
            time_wrong.innerText = result_date
        }else if(durationText.includes(".")){
            time_wrong.innerText = Number(durationText).toLocaleString('en-US',{ maximumFractionDigits: 2, minimumFractionDigits: 2 })
        }
        else{
            if(durationText!="0"){
            time_wrong.innerText = durationText.slice(0,-3)
            }else{
                time_wrong.innerText = Number(durationText).toLocaleString('en-US',{ maximumFractionDigits: 2, minimumFractionDigits: 2 })
            }
        }
    }
    for (let fuel_format of fuel_formats){
        fuel_format.innerText = Number(fuel_format.innerText).toLocaleString('en-US',{ maximumFractionDigits: 2, minimumFractionDigits: 2 })
    }
    excavators[0].style.display = "none";
    reportTable.style.display = "";
}else if (window.location.href.endsWith('/import')){
    console.log("nani")

    let d = new Date();

    let hour = d.getHours();
    let minute = d.getMinutes();

    function changeTheTime(sth,threshold){
        threshold = Number(threshold)
        if (sth.value > threshold) {
            sth.value = threshold;
        } else if (sth.value < 0) {
            sth.value = '00';
        }else if((sth.value.length > 2) && sth.value.startsWith('0')){
            sth.value = sth.value.slice(sth.value.length-2)
            console.log(sth.value.slice(sth.value.length-2))
        }

        if (sth.value == "") {
            if (threshold == 23){
                sth.value = formatTime(hour);
            }else if(threshold == 59){
                sth.value = formatTime(minute)
            }
            
        }
        sth.value = formatTime(sth.value)
    }


    function formatTime (time) {
        if (time < 10 && time.length == 1) {
            time = '0' + time;
        }
        return time;
    }
}

/* show animation */
function showTruckAnimation(){
    let dataExpenseContainer = document.getElementById("duty-expense-container")
    dataExpenseContainer.classList.add("demo")
    const animator = document.getElementsByClassName("sending-container")[0]
    animator.classList.remove("d-none")
}

/* Export */
function exportTableToExcel(tableId) {
    const table = document.getElementById(tableId);

    headerRows = table.querySelectorAll('tr.d-none')
    headerRows.forEach(row=>{
        row.classList.remove('d-none')
    })

    const wb = XLSX.utils.table_to_book(table, { sheet: "SheetJS" });
    const wbout = XLSX.write(wb, { bookType: "xlsx", type: "array" });
    const blob = new Blob([wbout], { type: "application/octet-stream" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "Export-Data.xlsx";
    a.click();
    URL.revokeObjectURL(url);

    headerRows.forEach(row=>{
        row.classList.add('d-none')
    })
}

function exportTablesToExcel(tableId_one,tableId_two,tableId_three) {
    const wb = XLSX.utils.book_new();

    // Combine the data from all tables into one array
    let combinedData = [];

    for (const tableId of [tableId_one,tableId_two,tableId_three]) {
    const table = document.getElementById(tableId);
    const tableData = XLSX.utils.table_to_sheet(table);

    // Get the data as an array of arrays and add to the combinedData array
    const dataArray = XLSX.utils.sheet_to_json(tableData, { header: 1 });
    combinedData = combinedData.concat(dataArray);
    }

    // Create a new worksheet with the combined data
    const worksheet = XLSX.utils.aoa_to_sheet(combinedData);

    // Add the worksheet to the workbook
    XLSX.utils.book_append_sheet(wb, worksheet, "CombinedSheet");
  
    // Export the workbook as a single Excel file
    const wbout = XLSX.write(wb, { bookType: "xlsx", type: "array" });
    const blob = new Blob([wbout], { type: "application/octet-stream" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "Exported_Tables.xlsx";
    a.click();
    URL.revokeObjectURL(url);
  }


  
  

/* responsive and media query */
function updateInputSize() {
    const inputElement = document.getElementById('inputForProjectInMonthly');
    if (window.innerWidth <= 767) { // Change size for smaller screens (e.g., phones)
        inputElement.setAttribute('size', '18');
    }
}
  
  // Call the function initially to set the correct size based on the screen size
updateInputSize();
  
  // Add an event listener to update the size when the screen is resized
window.addEventListener('resize', updateInputSize);
  
function addInput(addBtn,typ='add'){
    var hiddenInp = addBtn.parentElement.parentElement.previousElementSibling
    if (typ == 'add'){
        addBtn.nextElementSibling.classList.remove("d-none") 
        hiddenInp.classList.remove("d-none") 
        addBtn.classList.add("d-none")        
    }else{
        addBtn.classList.add("d-none")  
        hiddenInp.classList.add("d-none")
        addBtn.previousElementSibling.classList.remove("d-none")         
    }
}

function saveMachineToProjectStats(save){
    const tbody = save.parentElement.parentElement.parentElement.parentElement;
    const inputTr = save.parentElement.parentElement.parentElement;
    const machineName = save.parentElement.children[0].value.replace("/","thisIsSlash").trim();
    console.log(save.parentElement.children[1].value,typeof save.parentElement.children[1].value)
    const manPower = save.parentElement.children[1].value.replace("e","").trim();
    console.log(manPower)
    if(inputTr.children[0].classList.contains("mechanicianInp")){
        if(!machineName == "" && manPower > 0){
            fetch(`/get-api/employee-group-check/${machineName}`)            
            .then(response => response.json())
            .then(result => {
                if (result.length == 0){
                    alert("Invalid Employee Grop Name")
                }else{
                    let has_error = false;
                    let all_ids = document.querySelectorAll(".employee_group_id")
                    if (all_ids){
                        for (let eachID of all_ids){
                            if (eachID.value == result[0][0]){
                                alert("Employee Group is already existed in this project ... ")
                                has_error = true
                                break
                            }   
                        }
                    }
                    if (!has_error){
                        const newTr = document.createElement("tr");
                        newTr.className = "text-center fs-6";
                        newTr.innerHTML = `
                                        <td>${result[0][1]} <input type='number' class='employee_group_id' value='${result[0][0]}' hidden name='employee_group_id'/></td>
                                        <td>${manPower} <input type='number' class='employee_power_id' value='${manPower}' hidden name='employee_power'/></td>
                                        <td><button onclick='removeDataFromStats(this)' class="btn btn-sm btn-danger" type='button'>Remove</button></td>    
                                        `
                        tbody.insertBefore(newTr, inputTr);
                        save.parentElement.children[0].value = "";
                        save.parentElement.children[1].value = "";
                    }                    
                } 
            })
            .catch(err => console.log(err))
        }else{
            alert("Invalid Manpower Or Invalid Employee Type ...");
        }
    }else if(inputTr.children[0].classList.contains("meName")){
        if (machineName == ""){
            alert("Blank Machine Name")
        }else{
            fetch(`/get-api/machine-check/${machineName}`)
            .then(response => response.json())
            .then(result => {
                if (result.length == 0){
                    alert("Invalid Machine Name or Machine is Already in Another Project ..")
                }else{
                    let has_error = false;
                    let all_ids = document.querySelectorAll(".machine_id")
                    if (all_ids){
                        for (let eachID of all_ids){
                            if (eachID.value == result[0][0]){
                                alert("Machine is already existed in this project ... ")
                                has_error = true
                                break
                            }   
                        }
                    }
                    if (!has_error){
                        const newTr = document.createElement("tr");
                        newTr.className = "text-center fs-6";
                        newTr.innerHTML = `
                                        <td>${result[0][1]} <input type='number' class='machine_id' value='${result[0][0]}' hidden name='machine_id'/></td>
                                        <td>${result[0][2]}</td>
                                        <td><button class="btn btn-sm btn-success me-2" type='button'>Transfer</button><button class="btn btn-sm btn-danger" type='button' onclick='removeDataFromStats(this)'>Remove</button></td>    
                                        `
                        tbody.insertBefore(newTr, inputTr);
                        save.parentElement.children[0].value = "";
                        save.parentElement.children[1].value = "";
                    }                    
                } 
            })
            .catch(err => console.log(err))
        }
    };
}

function removeDataFromStats(btn){
    btn.parentElement.parentElement.remove()
}

function checkProjectAndReplaceId(inp,idd){
    let pj_code = inp.value.split("|")[0].replace("/","thisIsSlash").trim()
    console.log(pj_code)
    let url_route = 'project-check-for-stats'
    if (idd = 'transfer_project_id_for_stat'){
        url_route = 'project-check-for-transfer-stats'
    }
    fetch(`/get-api/${url_route}/${pj_code}`)
    .then(response => response.json())
    .then(result => {
        let pj_id_holder = document.getElementById(idd)
        console.log(result)
        if (result.length == 0){
            pj_id_holder.value = ""
            pj_id_holder.setAttribute("required","")
        }else{
            pj_id_holder.value = result[0][0]
            pj_id_holder.removeAttribute("required")                    
        } 
    })
    .catch(err => console.log(err))
}

function redirectToProjectStatForm(inp_id,form_id,val){
    document.getElementById(inp_id).value = val
    document.getElementById(form_id).submit()
}

function editPrjStatis(editBtn,selectId){
    const prjStatis = document.querySelector(`#${selectId}`);
    const getInp = prjStatis.querySelectorAll("input[disabled]");
    const getBtn = prjStatis.querySelectorAll("button[disabled]")
    const editSubmitPjStat = document.getElementById("edit-submit-btn-pj-stat")
    for(let i = 1; i < getInp.length; i++){
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
    editSubmitPjStat.classList.remove("d-none")
    editBtn.previousElementSibling.classList.remove("d-none")
}

function savePrjStatis(saveBtn){
    location.reload();
}

function directlyremoveDataFromStats(api_id,btn){
    let api_call = ""
    if (btn.classList.contains("emp-data")){
        api_call = 'delete-employee-group-history'
    }else{
        api_call = 'delete-machines-histrory'
    }
    fetch(`/get-api/${api_call}/${api_id}`)
    .then(response => {
        if (response.status == 200){
            alert("Successful deleting..")
            btn.parentElement.parentElement.remove()
        }else{
            alert("Unknow error occurred while deleting ..")
        }
    })
}

function replaceIdInTheTransferModal(hisId,machine_id){
    document.getElementById("source-history-id").value = hisId
    document.getElementById("source-machine-id").value = machine_id
}

function submitMachineTransferForStat(){
    his_id = document.getElementById("source-history-id").value.trim()
    project_id = document.getElementById("transfer_project_id_for_stat").value.trim()
    start_time = document.getElementById("transfer_machine_stat").value.trim()
    machine_id = document.getElementById("source-machine-id").value.trim()
    console.log(his_id,project_id,start_time,machine_id)
    if (his_id == '' || project_id == '' || start_time == '' || machine_id == ''){
       alert("Incomplete Datas") 
    }else{
        fetch(`/get-api/transfer_machine_project/${his_id}~~${project_id}~~${start_time}~~${machine_id}`)
        .then(response => {
            if(response.status == 200){
                console.log("Success")
                document.getElementById("submitMachineTransferForStatCloseBtn").click()
            }else{
                alert("Unknown error occurred...")
            }
        })     
    }

}

function checkValidMachine(inp,idd,mandatory=true){
    let allMachineDatas = document.querySelectorAll(`#${idd} option`)
    let found = ""
    allMachineDatas.forEach(opt => {
        if(opt.value == inp.value){
            found = opt.getAttribute("getId")
        }
    })
    inp.previousElementSibling.value = found
    if (found == ""){
        if (mandatory){
            inp.previousElementSibling.setAttribute("required","")
        }
        inp.value = ""
    }else{
        inp.previousElementSibling.removeAttribute("required")
    }
}

function setDbAndGiveProjectCodes(for_what){
    giveProjectCodes('aboveProjectCodesForExport')
    document.getElementById("db_model").value = for_what.trim()
}



function createEmp(btn){
    const getInp = document.getElementById("emplyInp");
    const discardBtn = document.getElementById("discardBtn");
    getInp.classList.remove("d-none");
    discardBtn.classList.remove("d-none");
    btn.classList.add("d-none");
}

function discardEmp(btn){
    const getInp = document.getElementById("emplyInp");
    const createBtn = document.getElementById("createBtn");
    getInp.querySelectorAll("input").forEach(inp => {
        inp.value = ""
    })
    getInp.classList.add("d-none");
    createBtn.classList.remove("d-none");
    btn.classList.add("d-none");
}

function replaceDataRedirectSummaryForm(pj_id,pj_name){
    let submitForm = document.getElementById("autoRedirectSummary")
    submitForm.children[0].value = pj_id
    submitForm.children[1].value = pj_name
    submitForm.submit()
}