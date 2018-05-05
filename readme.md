SSO(Single Sign On)
===================

##### 单点登录
    在一个多系统共存的环境下，用户在一处登录后，就不用在其他系统中登录。
    一次登录，多处访问。

##### 前端实现
    cookie 无法跨域
    localstorage 也无法跨域
    a.com 和 b.com 通过 iframe 引入一个共同的 c.com 页面
    在 c.com 域名下，通过 window.postMessage() 读写 localstorage
    在 a.com 下登录成功后， localstorage 中保存一个 token
    去 b.com 访问时，拿到这个 token ，发送给 sso ， sso 进而去查询用户是否已经登录
    [详细操作](http://blog.csdn.net/sflf36995800/article/details/53290457)
        