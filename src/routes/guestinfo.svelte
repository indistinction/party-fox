<style>

    h2{
        margin: 24px 0 0;
    }

    .logosmall{
        display: block;
        width: 180px;
        margin: 0 auto;
        padding: 64px 0 0;
        box-sizing: border-box;
    }

    .head {
        display: block;
        width: 100%;
        text-align: center;
        padding: 32px 0 0;
        margin: 0;
    }

    .container {
        margin: 0 auto;
        padding: 16px 12px;
        max-width: 600px;
        -webkit-transition-duration: 600ms;
        transition-duration: 600ms;
    }

    .section {
        text-align: center;
        margin: 0 0 64px;
    }

    /*.vspacer {
        height: 128px;
    }


    .button-bar {
        text-align: center;
        margin: 36px 0 0;
    }

    .button-bar button {
        min-width: 100px;
    }

    .spinny-button{
        margin:0 0 12px 0;
        display:inline-block;
        width:100px;
        height:48px;
        padding:8px 0;
        box-sizing: border-box;
        vertical-align: top;
    }*/
</style>

<script>
  import queryString from "query-string";
  import { onMount } from 'svelte';

  let months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  let settings = {
    backend: "http://127.0.0.1:8000",
    //backend: "https://a.amazonaws.com/api",
  }
  let dynamKey = "";
  let data = {PK:"", email: "", address:""}

  function formatDate(dateString){
    let dateParts = dateString.split("#")
    let dmy = dateParts[0].split("-")
    return `${dmy[2]} ${months[parseInt(dmy[1])]} ${dmy[0]} at ${dateParts[1]}`
  }

  function saveGuest(){
    data.status = "3"
    fetch(`${settings.backend}/guest/${encodeURIComponent(data.PK)}/${encodeURIComponent(data.SK)}/${encodeURIComponent(data.accessKey)}`, {
      method: 'post',
      headers: {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    }).then(function(response) {
      if (response.status === 204){
        console.log("OK")
      } else {
        console.log("FAIL")
        // TODO Emit error. There's a toast somewhere.
      }
    })
  }

  onMount(async () => {
    dynamKey = queryString.parse(window.location.search)["g"];
    fetch(`${settings.backend}/guestinfo/${dynamKey}`)
    .then(response => response.json())
    .then(rdata => {
      data = {...data, ...rdata}
      })
  });
</script>


<a href="/"><img src="/img/logo.png" class="logosmall" alt="party logo"></a>
<h1 class="head" id="anchor">Your Details</h1>

<div class="container">
    <div class="section">
        <p>{data.kidName} has been invited to {data.superstarName}'s online party on {formatDate(data.PK)} </p>
        <p>We'll email out the Zoom link in advance, so please confirm your email address below.</p>
        <input class="input"
               placeholder="Contact email for {data.kidName}"
               bind:value={data.email}
        />
        {#if data.box}
            <p>Before the party we'll send {data.kidName} a box of gifts and props. Please confirm the address you'd like this delivered to below.</p>
            <textarea class="input" rows="5" placeholder="{data.kidName}'s address" bind:value={data.address}></textarea>
        {/if}
        <button class="btn btn-purple btn-block"
                on:click={saveGuest()}
        >Save details</button>
    </div>
</div>