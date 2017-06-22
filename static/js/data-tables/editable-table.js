var EditableTable = function () {

    return {

        //main function to initiate the module
        init: function () {
            function restoreRow(oTable, nRow) {
                var aData = oTable.fnGetData(nRow);
                var jqTds = $('>td', nRow);

                for (var i = 0, iLen = jqTds.length; i < iLen; i++) {
                    oTable.fnUpdate(aData[i], nRow, i, false);
                    //这里判断输入框类型
                }

                oTable.fnDraw();
            }

            function editRow(oTable, nRow) {
                var aData = oTable.fnGetData(nRow);
                var jqTds = $('>td', nRow);
                jqTds[0].innerHTML = '<input type="text" class="form-control small" value="' + aData[0] + '">';
                jqTds[1].innerHTML = '<input type="text" class="form-control small" value="' + aData[1] + '">';
                jqTds[2].innerHTML = '<input type="text" class="form-control small" value="' + aData[2] + '">';
                jqTds[3].innerHTML = '<input type="text" class="form-control small" value="' + aData[3] + '">';
                jqTds[4].innerHTML = '<a class="edit" href="">Save</a>';
                jqTds[5].innerHTML = '<a class="cancel" href="">Cancel</a>';
            }

            function saveRow(oTable, nRow) {
                var jqInputs = $('input', nRow);
                oTable.fnUpdate(jqInputs[0].value, nRow, 0, false);
                oTable.fnUpdate(jqInputs[1].value, nRow, 1, false);
                oTable.fnUpdate(jqInputs[2].value, nRow, 2, false);
                oTable.fnUpdate(jqInputs[3].value, nRow, 3, false);
                oTable.fnUpdate('<a class="edit" href="">Edit</a>', nRow, 4, false);
                oTable.fnUpdate('<a class="delete" href="">Delete</a>', nRow, 5, false);
                oTable.fnDraw();
            }

            function cancelEditRow(oTable, nRow) {
                var jqInputs = $('input', nRow);
                oTable.fnUpdate(jqInputs[0].value, nRow, 0, false);
                oTable.fnUpdate(jqInputs[1].value, nRow, 1, false);
                oTable.fnUpdate(jqInputs[2].value, nRow, 2, false);
                oTable.fnUpdate(jqInputs[3].value, nRow, 3, false);
                oTable.fnUpdate('<a class="edit" href="">Edit</a>', nRow, 4, false);
                oTable.fnDraw();
            }

            var oTable = $('#editable-sample').dataTable({
                "aLengthMenu": [
                    [5, 15, 20, -1],
                    [5, 15, 20, "All"] // change per page values here
                ],
                // set the initial value
                "iDisplayLength": 5,
                "sDom": "<'row'<'col-lg-6'l><'col-lg-6'f>r>t<'row'<'col-lg-6'i><'col-lg-6'p>>",
                "sPaginationType": "bootstrap",
                "oLanguage": {
                    "sLengthMenu": "_MENU_ records per page",
                    "oPaginate": {
                        "sPrevious": "Prev",
                        "sNext": "Next"
                    }
                },
                "aoColumnDefs": [{
                        'bSortable': false,
                        'aTargets': [0]
                    }
                ]
            });

            jQuery('#editable-sample_wrapper .dataTables_filter input').addClass("form-control medium"); // modify table search input
            jQuery('#editable-sample_wrapper .dataTables_length select').addClass("form-control xsmall"); // modify table per page dropdown

            var nEditing = null;

            $('#editable-sample_new').click(function (e) {
                e.preventDefault();
                var aiNew = oTable.fnAddData(['', '', '', '','','',
                        '<a class="edit" href="">Edit</a>', '<a class="cancel" data-mode="new" href="">Cancel</a>'
                ]);
                var nRow = oTable.fnGetNodes(aiNew[0]);
                editRow(oTable, nRow);
                nEditing = nRow;
            });

            $('#editable-sample a.delete').live('click', function (e) {
                e.preventDefault();

                if (confirm("Are you sure to delete this row ?") == false) {
                    return;
                }

                var nRow = $(this).parents('tr')[0];
                oTable.fnDeleteRow(nRow);
                alert("Deleted! Do not forget to do some ajax to sync with backend :)");
            });

            $('#editable-sample a.cancel').live('click', function (e) {
                e.preventDefault();
                if ($(this).attr("data-mode") == "new") {
                    var nRow = $(this).parents('tr')[0];
                    oTable.fnDeleteRow(nRow);
                } else {
                    restoreRow(oTable, nEditing);
                    nEditing = null;
                }
            });

            $('#editable-sample a.edit').live('click', function (e) {
                e.preventDefault();

                /* Get the row as a parent of the link that was clicked on */
                var nRow = $(this).parents('tr')[0];

                if (nEditing !== null && nEditing != nRow) {
                    /* Currently editing - but not this row - restore the old before continuing to edit mode */
                    restoreRow(oTable, nEditing);
                    editRow(oTable, nRow);
                    nEditing = nRow;
                } else if (nEditing == nRow && this.innerHTML == "Save") {
                    /* Editing this row and want to save it */
                    saveRow(oTable, nEditing);
                    nEditing = null;
                    alert("Updated! Do not forget to do some ajax to sync with backend :)");
                } else {
                    /* No edit in progress - let's start one */
                    editRow(oTable, nRow);
                    nEditing = nRow;
                }
            });
        }

    };

}();/**
 * Created by DaoKe on 16/8/1.
 */

entry_type = [
    {'id':1,text:'A'},
    {'id':2,text:'CNAME'},
    {'id':3,text:'NS'},
    {'id':4,text:'AAAA'},
    {'id':5,text:'显性URL'},
    {'id':5,text:'隐形URL'}
]

entry_line = [
    {'id':1,text:'默认'},
    {'id':2,text:'四川'}
]

//页面加载完成后执行

$(function(){
    $('#tb1').find(':checkbox').click(function () {
        console.log(123)
        var tr = $(this).parent().parent(); // 找到tr
        if($("#edit_mode").hasClass('editing')){
            if ($(this).prop('checkend')){
                //当前行进入编辑状态
                console.log('456')
                RowIntoEdit(tr);
            }else{
                //当前行退出编辑状态
                RowOutEdit(tr)
            }
        }
    })
})





function CheckSave(mode,tb){
    //1.遍历table,检测每一行,如果checkbox选中,提交当前行数据到后台;
    data = []
    $(tb).children().each(function(){
        var tr = $(this);
        var isChecked = tr.find(':checkbox').prop('checked');
        var id = tr.find(':checkbox').val()
        if (isChecked==true){
            //找到选中的行;
            isEditMode = $(mode).hasClass('editing');
            if (isEditMode){
                //循环每个td的数据
                var td_data = {'id':id};
                tr.children().each(function(){
                    var td = $(this);
                    if (td.attr('edit') == 'true') {
                        inp = td.children(':first');
                        console.log(id + ':' + td.attr('name') + ':'  + inp.val())
                        td_data[td.attr('name')] = inp.val()
                    }
                });
                console.log(td_data)
                //ajax(td_data);提交数据
            }else{
                alert('未编辑状态,不能提交数据');
                return false ;
            }
        }
    })
}

function CheckAll(mode,tb){
    //1.选中checkbox
    //2.如果已经进入编辑模式,让选中行进入编辑状态
    //$(tb) = $('$tb1')
    $(tb).children().each(function(){
        //$(this) 表示循环过程中每一个tr
        var tr = $(this)
        var isChecked = $(this).find(':checkbox').prop('checked');
        if (isChecked==true){

        }
        else{
            $(this).find(':checkbox').prop('checked',true);
            //如果已经进入编辑模式,让选中行进入编辑状态
            var isEditMode = $(mode).hasClass('editing');
            if (isEditMode){
                //让行进入编辑状态;
                //tr.children().each(function(){
                //    var td = $(this);
                //    //判断这行是否允许被编辑;我们设置属性edit=true
                //    if (td.attr('edit')=='true'){
                //        //当前行进如编辑状态
                //        var text = td.text();
                //        var temp = "<input type='text' value='"+text+"'/>";
                //        td.html(temp);
                //    }
                //})
                RowIntoEdit(tr);
            };
        }

    })
}

function RowOutEdit(tr){
    //推出行编辑模式
    tr.children().each(function(){
        var td = $(this);
        if (td.attr('edit') == 'true'){
            //还可继续判断标签类型 input ,select等等
            var inp = td.children(':first') //找到第一个孩子 <input />标签 或者select标签
            var input_value = inp.val();
            td.text(input_value);
        }
    })
}

function RowIntoEdit(tr){
    //行进入编辑模式
    tr.children().each(function(){
        var td = $(this);
        //判断这行是否允许被编辑;我们设置属性edit=true
        if (td.attr('edit')=='true'){
            //当前行进如编辑状态

            if(td.attr('edit-type')=="select"){
                //判断当前行类型
                //通过属性 name来判断不同的select类型
                var all_values = window[td.attr('name')];
                var options = "";
                var sel_val = td.attr('sel-val');//获取属性sel-val select当前的value值
                sel_val = parseInt(sel_val);  //转换成int
                $.each(all_values,function(index,value){//遍历数组的时候,第一个参数为下标,第二个下标为元素
                    //通过属性 sel-val 来判断select 当前select的value
                    if (sel_val == value.id){
                        options += "<option selected='selected'>" + value.text + "</option>";
                    }else {
                        options += "<option>" + value.text + "</option>";
                    }
                });
                var temp = "<select>" + options + "</select>"
                td.html(temp)

            }else {
                var text = td.text();
                var temp = "<input type='text' value='" + text + "'/>";
                td.html(temp);
            }
        }
    })
}

function CheckReverse(mode,tb){
    //1.是否处于编辑模式
    //2.是否选中
    if ($(mode).hasClass('editing')){
        $(tb).children().each(function(){
            var tr = $(this);
            var check_box = tr.children().first().find(':checkbox');
            if (check_box.prop('checked')){
                //取消选中
                check_box.prop('checked',false);
                //退出行编辑模式;
                RowOutEdit(tr);
            }else{
                //反选
                check_box.prop('checked',true);
                RowIntoEdit(tr);
            }
        });

    }else{
        $(tb).children().each(function(){
            //取消选中即可
            var tr = $(this);
            var check_box = tr.children().first().find(':checkbox');
            if (check_box.prop('checked')){
                //取消选中
                check_box.prop('checked',false);
            }else{
                //反选
                check_box.prop('checked',true);
            }

        })

    }
}


function CheckCancel(mode,tb){
    //1.取消选中checkbox
    //2.如果已经进入编辑模式,行退出编辑状态
    $(tb).children().each(function(){
        var tr = $(this);
        if (tr.find(':checkbox').prop('checked')){
            //移除选中状态;
            console.log(tr)
            tr.find(':checkbox').prop('checked',false);

            var isEditing = $(mode).hasClass('editing');
            if (isEditing == true){
                // 当前行,退出编辑状态
                tr.children().each(function(){
                    var td = $(this);
                    if (td.attr('edit') == 'true'){
                        var inp = td.children(':first') //找到第一个孩子 <input />标签
                        var input_value = inp.val();
                        td.text(input_value);
                    }
                })
            }

        }
    })
}



/*进入编辑模式:
    遍历table,检测每一行,如果checkbox选中,当前行进入编辑状态
  退出编辑模式:
    遍历table,检测每一行,如果选中,退出编辑模式
*/
function EditMode(ths,tb){
    //ths = this
    var isEditing = $(ths).hasClass('editing');
    if (isEditing){
        //退出编辑模式
        $(ths).removeClass('editing');
        $(ths).text('进入编辑模式');
        $(tb).children().each(function(){
            var tr = $(this);
            if (tr.find(':checkbox').prop('checked')){
                //当前行退出编辑状态;
                tr.children().each(function(){
                    var td = $(this);
                    if (td.attr('edit') == 'true'){
                        var inp = td.children(':first');
                        var input_value = inp.val();
                        td.text(input_value);

                    }
                });

            }
        });
    }
    else{
        //进入编辑模式
        $(ths).addClass('editing');
        $(ths).text('退出编辑模式');
        $(tb).children().each(function(){
            var tr = $(this);
            var isCheckbox = tr.find(':checkbox').prop('checked');
            if (isCheckbox == true){
                //当前行进入编辑状态
                //tr.children().each(function(){
                //    var td=$(this);
                //    if (td.attr('edit')=='true'){
                //        if(td.attr('edit-type')=="select") {
                //            //判断当前行类型
                //            var temp = "<select><option>在线</option><option>离线</option></select>"
                //            td.html(temp)
                //        }else {
                //            var text = td.text();//www
                //            var temp = "<input type='text' value='" + text + "'>";
                //            td.html(temp);
                //        }
                //    }
                //})
                RowIntoEdit(tr);
            }
        })
    }
}