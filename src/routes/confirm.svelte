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

    let settings = {
        backend: "http://127.0.0.1:8000",
        //backend: "https://xxx.amazonaws.com/api",
    }

    let dynamKey = "";
    let data = {guests:[]};
    let addresses = {}
    let superstarInfo = ""
    let emails = {}
    let phones = {}
    let selectEmailMobile = {}

    function updateGuest(slot, guest, akey, newdata){

        for (const property in newdata) {
            if (newdata[property] === null){
                delete newdata[property]
            }
        }

        fetch(`${settings.backend}/guest/${encodeURIComponent(slot)}/${encodeURIComponent(guest)}/${encodeURIComponent(akey)}`, {
            method: 'post',
            headers: {
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newdata)
        }).then(function(response) {
            if (response.status === 204){
                console.log("OK")
                data.guests.forEach(guest => {
                    if (guest.SK === newdata.SK){
                        for (var attrname in newdata) { guest[attrname] = newdata[attrname] }
                    }
                })
            } else {
                console.log("FAIL")
                // TODO Emit error. There's a toast somewhere.
            }
        })
    }

    onMount(async () => {
        dynamKey = queryString.parse(window.location.search)["b"];
        fetch(`${settings.backend}/confirm/${dynamKey}`)
            .then(response => response.json())
            .then(rdata => {
                data = rdata
                data.guests.forEach(guest => {
                    addresses[guest.SK] = ""
                    emails[guest.SK] = ""
                    phones[guest.SK] = ""
                    selectEmailMobile[guest.SK] = "E"
                })
            });
    });


</script>

<a href="/"><img src="/img/logo.png" class="logosmall" alt="party around logo"></a>
<h1 class="head" id="anchor">Booking Details</h1>

<div class="container">
    <div class="section">
        <p>Now your booking has been confirmed we can start planning your party!</p>

        <p>Obviously the most important thing is that we know where to send the party boxes.</p>

        <p>If you know the address that you would like to send each guest's box to, please enter it in the below and click save.
            If you don't know their address please enter an email address and we will contact them directly with an invitation. </p>

        <p>You can update this information any time up to 10 days before the party.</p>
    </div>

    {#each data.guests as guest, i}
        <div class="section">
            {#if guest.isSuperstar}
                <h2>Superstar: {guest.kidName}</h2>
                <textarea class="input" rows="5" placeholder="Tell us a little bit more about {guest.kidName}. Do they have any hobbies or interests? Who are their close friends, family members, or pets? What about favourite TV shows or movies? More information means a more personal party!" bind:value={superstarInfo}></textarea>
            {:else}
                <h2>Guest {`${i}`}: {guest.kidName}</h2>
            {/if}
                {#if guest.status === "0"}
                    {#if guest.box}
                        <textarea class="input" rows="5" placeholder="{guest.kidName}'s postal address" bind:value={addresses[guest.SK]}></textarea>
                        <button class="btn btn-purple btn-block"
                                on:click={updateGuest(guest.PK, guest.SK, guest.accessKey, {"address": addresses[guest.SK], "status":"3"})}
                        >Save details</button>
                        <p>Don't have {guest.kidName}'s address? Send them an invite and we'll do the rest!</p>
                    {:else}
                        <p>You haven't booked a party box for {guest.kidName}, but you can still send an invitation.</p>
                    {/if}
                    <select bind:value={selectEmailMobile[guest.SK]} class="input">
                        <option value="E">Send via email</option>
                        <option value="M">Send via mobile</option>
                    </select>
                    {#if selectEmailMobile[guest.SK] == "E"}
                    <input class="input"
                           placeholder="Contact email for {guest.kidName}"
                           bind:value={emails[guest.SK]}
                           disabled="{phones[guest.SK].length > 0}"
                    />
                    {:else}
                    <input class="input"
                           placeholder="Contact mobile phone number for {guest.kidName}"
                           bind:value={phones[guest.SK]}
                           disabled="{emails[guest.SK].length > 0}"
                    />
                    {/if}
                    <!-- TODO add user message that can be one or toher -->
                    <button class="btn btn-purple btn-block"
                            on:click={
                                updateGuest(guest.PK, guest.SK, guest.accessKey, {
                                "email": emails[guest.SK].length > 0 ? emails[guest.SK] : null,
                                "mobile": phones[guest.SK].length > 0 ? phones[guest.SK] : null,
                                "status": emails[guest.SK].length > 0 ? "1" : (phones[guest.SK].length > 0 ? "2" : null)
                            })}
                    >Send invitation</button>
                {:else if guest.status === "1"}
                    <p>We've sent {guest.kidName} an email invitation{#if guest.box}, but we're still waiting to for their address confirmation - you might like to chase this up with them{/if}.</p>
                {:else if guest.status === "2"}
                    <p>We've sent {guest.kidName} a text invitation{#if guest.box}, but we're still waiting to for their address confirmation - you might like to chase this up with them{/if}.</p>
                {:else if guest.status === "3"}
                    <p>{guest.kidName} has received their invitation and confirmed their details. Great!</p>
                {:else}
                    <p>Hmm. There's been a problem checking this guest's details. Please contact us via email to look into this.</p>
                {/if}
        </div>
    {/each}

</div>