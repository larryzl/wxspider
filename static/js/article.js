/**
 * Created by lei on 2019/8/14.
 */

function showArticle(id,csrf){
    var post_url = "/api/manager/get/article";
    var post_data = {'kind':id};
    var article_html = '';
    $.ajaxSetup({data: {csrfmiddlewaretoken:csrf}});
    $.ajax({
        type:'post',
        url:post_url,
        data:post_data,
        dataType:'json',
        success: function(data){
            if(data.code == 200){
                $.each(data.msg,function(index,element){
                    article_html += '<div class="col-lg-8"><div class="card alert"><div class="card-header"><h3><a href="">'+
                        element['title']+'</a></h3></div><div class="card-body"><p class="text-muted m-b-15">'+ element['abstract']+'</p></div><p><b>'+
                        element['gzh']+'</b>   '+element['publish_time']+'</p></div></div><div class="col-lg-3"><div class="card alert">'+
                        '<img src="'+element['avatar']+'"class=" img-responsive" alt="Cinque Terre"></div></div>';
                    document.getElementById('card-body').innerHTML = article_html;
                })
            }
        }
    })
}

function updateLabel(data){
    var
        $this = $(this),
        url = "/api/manager/update/article/kind"
        ;
    swal({
        title: '确定更新当前标签吗？',
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
            $.ajaxSetup({data: {csrfmiddlewaretoken: data.csrf}});
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
                            title:'更新完成',
                            type: 'success'
                            //html: '更新完成'
                        }).then(function(){
                            window.location.reload()
                        });
                    }else{
                        swal(
                            '更新失败',
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

function pullArticle(data){
    var
        $this = $(this),
        kind_id,
        kind_name,
        url = "/api/manager/pull/hot/article"
        ;
    if(data.is_all == true){
        kind_id = 'all',kind_name='全部分类';
    }else{
        $(".nav-item").each(function(){
            var y = $(this);
            if(y.hasClass('active') == true){
                kind_id = y.children().attr('id');
                kind_name = y.children().text();
                return false;
            }
        });
    }
    swal({
        title: '请选择爬取文章数量',
        html:
        '确定要爬取分类为<b style="font-size: 30px;color: #e70001;">'+kind_name+'</b>的文章吗？',
        type: 'question',
        input: 'range',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: '确定！',
        inputAttributes: {
            min: 1,
            max: 50,
            step: 1
        },
        inputValue: 10
    }).then(function(value){
        if(value.value){
            $.ajaxSetup({data: {csrfmiddlewaretoken: data.csrf}});
            $.ajax({
                type: 'post',
                url: url,
                data: {
                    'kind':kind_id,
                    'pull_num':value.value
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
        }else{
            swal('已取消','','error');
        }
    })
}
