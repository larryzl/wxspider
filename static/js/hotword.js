/**
 * Created by lei on 2019/8/14.
 */

function pullHotword(csrf){
    var
        url = "/api/manager/update/hotword",
        $this = $(this)
        ;
    swal({
        title: '确定爬取当前热词吗？',
        text: '更新期间不要关闭我哦！',
        type: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        confirmButtonClass: 'btn btn-success',
        cancelButtonClass: 'btn btn-danger',
        buttonsStyling: false
    }).then(function(value) {
        console.log(value);
        if(value.value){
            $.ajaxSetup({data: {csrfmiddlewaretoken: csrf}});
            $.ajax({
                type: 'post',
                url: url,
                dataType: 'json',
                beforeSend: function () {
                    $this.layerIndex = layer.load(0, {shade: [0.5, '#fff']});
                },
                success: function (data) {
                    if(data.code == 200){
                        swal({
                            title:'爬取完成',
                            type: 'success',
                            html: '共成功爬取文章:<b style="font-size: 15px;color: #e70001;">'+data.msg+'</b>条'
                        }).then(function(){
                            window.location.reload()
                        });
                    }else{
                        swal(
                            '爬取失败',
                            '错误原因:'+data.msg,
                            'error'
                        );
                    }
                },
                complete: function () {
                    layer.close($this.layerIndex);
                }
            })
        }else {
            swal('已取消','','error');

        }
    })
}

function initTable(csrf){
    // 表格选项
    var options = {
        ele : $("#datatable"),
        pageLength : 10,
        csrf: csrf,
        columnDefs: [
            {
                targets: 2,
                orderable: false,
                createdCell: function(td,cellData){
                    $(td).html('<a class="btn btn-xs btn-success" href="'+cellData+'" target="view_window">点击查看</a>');
                }
            },
            {
                targets : -1,
                orderable: false,
                createdCell: function(td,cellData,rowData){
                    $(td).html('<div class="btn-group btn-group-toggle"><button class="btn btn-xs btn-success m-l-xs btn_article_pull" data-url="'+ rowData.crawl_url + '" data-word="'+rowData.keyword+'">抓取</button> </div>');
                }
            }
        ],
        ajax_url: "/api/manager/get/hotword",
        columns: [
            { data: 'id'},
            { data: "keyword",orderable: false},
            { data: "crawl_url",orderable: false},
            { data: "article" },
            { data: "create_time" ,orderable: false},
             { data: 'intro',orderable:false,searchable:false}
        ]
    };
    var server_table = dt.initServerDataTable(options);
    return server_table
}


function pullKeywordArticle(data){
    var $this = $(this), url = "/api/manager/pull/keyword/article";
    swal({
        title: '确定爬取当前热词吗？',
        html: "<b style='color: #ff392b'>"+data.keyword+"</b>",
        type: 'warning',
        input: 'range',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: '确定！',
        inputAttributes: {
            min: 1,
            max: 20,
            step: 1
        },
        inputValue: 10
    }).then(function(value) {
        console.log(value);
        console.log(data.url);
        if(value.value){
            $.ajaxSetup({data: {csrfmiddlewaretoken: data.csrf}});
            $.ajax({
                type: 'post',
                url: url,
                data:{
                    keyword:data.keyword,
                    crawl_url:data.url,
                    crawl_num:value.value
                },
                dataType: 'json',
                beforeSend: function () {
                    $this.layerIndex = layer.load(0, {shade: [0.5, '#fff']});
                },
                success: function (data) {
                    if(data.code == 200){
                        swal({
                            title:'爬取完成',
                            type: 'success',
                            html: '共成功爬取文章:<b style="font-size: 15px;color: #e70001;">'+data.msg+'</b>条'
                        }).then(function(){
                            window.location.reload()
                        });
                    }else{
                        swal(
                            '爬取失败',
                            '错误原因:'+data.msg,
                            'error'
                        );
                    }
                },
                complete: function () {
                    layer.close($this.layerIndex);
                }
            })
        }else {
            swal('已取消','','error');

        }
    })
}
