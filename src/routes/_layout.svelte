<style>
    .footer{
        width: 100%;
        left: 0;
        bottom: 0;
        padding: 24px 16px;
        background: var(--purple);
        font-weight: bold;
        color: #fff;
        text-align: center;
        box-sizing: border-box;
        margin: 0;
        font-size: 10pt;
    }

    .social{
        height: 40px;

    }

</style>

<slot/>

<div class="footer">
    <a href="https://www.facebook.com/Party/" target="_blank">
        <img src="img/fb.png" class="social">
    </a>
    <a href="https://www.instagram.com/party_parties/" target="_blank">
        <img src="img/ig.png" class="social">
    </a>

</div>

<!-- For Sapper building -->
<div style="visibility: hidden; position: absolute">
    <a href="/book">book</a>
    <a href="/success">success</a>
    <a href="/admin">admin</a>
    <a href="/confirm">confirm</a>
</div>