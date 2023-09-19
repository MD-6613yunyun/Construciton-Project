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

function giveProjectCodes(){
    let abovePj = document.getElementById("aboveProjectCodes")
    abovePj.innerHTML = ""
    if (abovePj){
        fetch("/get-pj-datas")
        .then(response => response.json())
        .then(result => {
            for (const dt of result){
                abovePj.innerHTML += `<p class="m-1 ms-2" shopID="${dt[0]}" projectCode="${dt[2]}" onclick="assignShop(this)">${dt[1]} _&_ ${dt[2]}</p>`
            }
        })
        .catch(err => console.log(err))
    }
}

function checkSupervisor(){
    let modalBody = document.getElementById("inside-statistics-modal-body")
    modalBody.innerHTML = ""
    let siteSupervisors = document.getElementsByClassName('site-supervisors')
    let codeName = document.getElementById('exampleDataListCode')
    if (!codeName.value.includes('|')){
        modalBody.innerHTML += `<h4>Invalid Project Name / Code : <strong class='text-danger'> ${codeName.value}</strong></h4>`
    } else{
        let allSupervisors = ""
        for (let supervisor of siteSupervisors){
            allSupervisors += `${supervisor.value},`
        }
        if (allSupervisors.trim() != ","){
            let closeBtn = document.getElementById("inModalStatisticsClose")
            let submitBtn = document.getElementById("inModalStatistics");
            fetch(`/duty/check-supervisior/${allSupervisors.slice(0,-1)}`)
            .then(response => response.json())
            .then(result => {
                if (result.length != 0){
                    for (let name of result){
                        modalBody.innerHTML += `<h4>${name}</h4>`
                    }
                    modalBody.innerHTML += "Not exist in the supervisors.. Add those without consideration??"
                }else{
                    modalBody.innerHTML += 'Successful'
                    submitBtn.click()
                    closeBtn.click()
                }
            })
        }
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

clicker = document.getElementById("autoClicker")
modalUserMgs = document.getElementById("modalUserWarn")
if (modalUserMgs.innerHTML.trim() != "<strong>None</strong>"){
    clicker.click()
}



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
                  "dty":"duty-query-changeable",
              "machine":"machine-list-changeable",
              "expense":"expense-list-changeable"}
    all_tr = document.getElementsByClassName(target_mapp[target])
    if (txt == 'prev'){
        displayAmt = btn.nextElementSibling.textContent.trim().split("/")
        getTotal = displayAmt[1]
        last = displayAmt[0].split("-")[1]
        fst = Number(displayAmt[0].split("-")[0])
        if (fst != 1){
            fetch(`/offset-display/${target}/${fst-81}`)
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
            fetch(`/offset-display/${target}/${last}`)
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
    animator.style.display = ""
}

/* Export  */
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
  
/* responsive and media query */



