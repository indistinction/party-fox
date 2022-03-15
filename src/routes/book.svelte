<style>

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
        margin: 0 0 32px;
    }

    .host-box-wrap {
        display: flex;
    }

    .host-box {
        box-sizing: border-box;
        background: var(--purple);
        border-radius: 5px;
        margin: 6px;
        padding: 8px;
        width: 200px;
        color: #fff;
        text-align: center;
        transition: background-color 0.2s ease-in-out;
    }

    .host-box:hover {
        background: cornflowerblue;
    }

    .rounded {
        width: 100%;
    }

    @media only screen and (max-width: 600px) {
        .host-box-wrap {
            flex-wrap: wrap;
        }
        .host-box {
            width: 100% !important;
        }

    }

    .vspacer {
        height: 128px;
    }

    .naked {
        border: 0;
        width: 80%;
        outline: none;
    }

    .bin {
        float: right;
        color: #333;
        cursor: pointer;
        transition: color 0.1s ease-in-out;
    }

    .bin:hover {
        color: var(--red);
    }

    .button-bar {
        text-align: center;
        margin: 36px 0 0;
    }

    .button-bar button {
        min-width: 100px;
    }

    .receipt{
        padding: 24px;
        background: #fff;
        color: #333 !important;
        box-shadow: 5px 5px 5px #333;
        /*border: 2px solid #000;*/
        border-radius: 2px;
    }

    .spinny-button{
        margin:0 0 12px 0;
        display:inline-block;
        width:100px;
        height:48px;
        padding:8px 0;
        box-sizing: border-box;
        vertical-align: top;
    }
</style>

<script>
    let prices = {
        character: 20,
        party: 100,
        box1: 11,
        postage: 5,
    }
    let settings = {
        personLimit: 8,
        //backend: "http://127.0.0.1:8000",
        backend: "x.amazonaws.com/api",
        leadTimeDays: 10
        //leadTimeDays: 0
    }

    import { onMount } from 'svelte';
    import {fade} from 'svelte/transition'
    import { loadStripe } from '@stripe/stripe-js';

    let stripe = null

    let dateList = {}
    import Datepicker from '../components/Datepicker.svelte';
    //https://github.com/6eDesign/svelte-calendar
    let startDate = new Date();
    startDate.setDate(startDate.getDate() + settings.leadTimeDays)
    let endDate = new Date()
    endDate.setDate(startDate.getDate() + (26 * 7))
    // This is like roughly 6 months in advance?
    let dateFormat = '#{l} #{j} #{F} #{Y}';

    let triggered = false
    let spinner = false;
    let currentPage = 1;
    const patrolNames = [
        "Guest 1",
        "Guest 2",
        "Guest 3",
        "Guest 4",
        "Guest 5",
        "Guest 6",
        "Guest 7",
        "Guest 8",
        "Guest 9",
        "Guest 10"
    ]
    let data = {
        dateChosen: startDate,
        host: "",
        kidName: "",
        kidBox: true,
        guests: [{name:"", box:true}, {name:"", box:true}, {name:"", box:true}, {name:"", box:true}],
        timeslot: "(not selected)"
    };
    let timeslots = []
    let costs = {
        party:prices.party,
        boxes:0,
        postage:0
    }
    let boxBtns = 2

    function getTimes() {
        timeslots = []
        let dateslots = dateList[data.dateChosen.toISOString().split("T")[0]]
        for (const time in dateslots) {
            timeslots.push({id:time, available:dateslots[time]})
        }
    }

    function pay() {
        spinner = true;
        fetch(`${settings.backend}/checkout`, {
            method: 'post',
            headers: {
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        }).then(function(response) {
            return response.json();
        }).then(function(data) {
            stripe.redirectToCheckout({ sessionId: data.id })
            /*TODO onerror spinner = false;*/
        })
    }

    function setBoxes(option){
        boxBtns = option
        if (option === 0){
            for (const guest of data.guests) {
                guest["box"]=false
            }
            data.kidBox = false
        } else if (option === 1){
            for (const guest of data.guests) {
                guest["box"]=false
            }
            data.kidBox = true
        } else if (option === 2){
            for (const guest of data.guests) {
                guest["box"]=true
            }
            data.kidBox = true
        }
    }

    $: boxCount = data.guests.filter(guest => guest.box).length + (data.kidBox?1:0)
    $: costs.boxes = boxCount * prices.box1
    $: costs.postage = boxCount * prices.postage
    $: total = Object.values(costs).reduce((a, b) => a + b);

    onMount(async () => {
        stripe = await stripe.loadStripe('pk_live_accountpubkey', { stripeAccount: "acct_accountnumber"});
        fetch(`${settings.backend}/slots`)
            .then(response => response.json())
            .then(data => {
                dateList = data
                getTimes()
            });
    });


</script>
<a href="/"><img src="/img/logo.png" class="logosmall" alt="party logo"></a>
<h1 class="head" id="anchor">Plan your party</h1>
<div class="container">
    {#if currentPage === 1}
        <div class="section">
            <h2>Step 1: Choose your host</h2>
            <div class="host-box-wrap">
                <div class="host-box" on:click="{() => {currentPage = 2;data.host='Foxy';extra=true;costs.party=prices.party+prices.character;}}">
                    <img src="/img/foxy1.jpg" class="rounded" alt="the friendly fox">
                    <p><strong>The Friendly Fox</strong></p>
                    <p>Join our foxy friend on a forest themed dance adventure.</p>
                </div>
                <div class="host-box" on:click="{() => {currentPage = 2;data.host='Eliza';costs.party=prices.party+prices.character;}}">
                    <img src="/img/eliza.jpg" class="rounded" alt="the ice princess">
                    <p><strong>The Ice Princess</strong></p>
                    <p>Discover your own frozen powers with our snowy ice princess.</p>
                </div>
                <div class="host-box" on:click="{() => {currentPage = 2;data.host='Ellen';costs.party=prices.party;}}">
                    <img src="/img/ellen.jpg" class="rounded" alt="party host">
                    <p><strong>Ella</strong></p>
                    <p>She's just a normal girl who loves to dance!</p>
                </div>
            </div>
        </div>

    {:else if currentPage === 2}
        <div class="box">
            <h2>Step 2: When and who!</h2>
            <div class="section">
                <p>We would like to know who's going to be at the party. You can invite a maximum of 8 different households to share the private video link, and anyone can attend the party; friends or family, old or young, near or far away, people who'll dance along or people who's just like to watch the fun... Everyone is welcome!</p>

                <div class="section">
                    <p><strong>Who is the superstar of this party?</strong></p>
                    <input type="text" class="input" bind:value={data.kidName} placeholder="Type their name here"/>
                </div>
                <p><strong>Please select a date...</strong></p>
                <Datepicker
                        format={dateFormat}
                        highlightColor='#d61d2b'
                        dayBackgroundColor='#efefef'
                        dayTextColor='#333'
                        dayHighlightedBackgroundColor='#d61d2b'
                        dayHighlightedTextColor='#fff'
                        start={startDate}
                        end={endDate}
                        bind:selected={data.dateChosen}
                        on:dateSelected={getTimes}
                />

            </div>
            <div class="section">
                {#if timeslots.length === 0}
                    <div class="btn" style="background: #666;cursor:not-allowed;">
                        No spaces available on that date. Please contact us for further information.
                    </div>
                {:else}
                {#each timeslots as timeslot}
                    <button
                            class="btn btn-purple"
                            on:click={() => {data.timeslot = timeslot.id;}}
                            style={"margin: 0 3px;"+(!timeslot.available ? "background: #666;cursor:not-allowed;" : (data.timeslot === timeslot.id ? "background: var(--orange)" : ""))}
                            disabled={!timeslot.available}
                    >
                        {timeslot.id}
                    </button>
                {/each}
                {/if}
            </div>
            <div class="section">
                <div><strong>Who would you like to invite?</strong></div>
                <p>Add the names of each guest you would like to invite to the party. (Please check that they are available to join in on the date and time above.)</p>
                {#each data.guests as guest, i}
                    <div class="input" style="text-align: left;" in:fade>
                        <input type="text" class="naked" bind:value={guest.name} placeholder={patrolNames[i]}/>
                        <svg
                                width="21"
                                height="21"
                                viewBox="0 0 24 24"
                                fill="none"
                                xmlns="http://www.w3.org/2000/svg"
                                class="bin"
                                on:click={() => {if (data.guests.length > 0) {data.guests.splice(i, 1); data.guests = [...data.guests]}}}
                        >
                            <path
                                    fill-rule="evenodd"
                                    clip-rule="evenodd"
                                    d="M17 5V4C17 2.89543 16.1046 2 15 2H9C7.89543 2 7 2.89543 7 4V5H4C3.44772 5 3 5.44772 3 6C3 6.55228 3.44772 7 4 7H5V18C5 19.6569 6.34315 21 8 21H16C17.6569 21 19 19.6569 19 18V7H20C20.5523 7 21 6.55228 21 6C21 5.44772 20.5523 5 20 5H17ZM15 4H9V5H15V4ZM17 7H7V18C7 18.5523 7.44772 19 8 19H16C16.5523 19 17 18.5523 17 18V7Z"
                                    fill="currentColor"
                            />
                            <path d="M9 9H11V17H9V9Z" fill="currentColor"/>
                            <path d="M13 9H15V17H13V9Z" fill="currentColor"/>
                        </svg>
                    </div>
                {/each}
                {#if data.guests.length < 20}
                    <button class="btn btn-block"
                            on:click={() => {if (data.guests.length < settings.personLimit) {data.guests = [...data.guests, {name: "", box:true}]}}}
                            style="background: var(--purple);"
                    >Add a guest
                    </button>
                {:else}
                    <div class="btn" style="background: #666; ">Max {settings.personLimit} guests!</div>
                {/if}
            </div>

            <div class="button-bar">
                <button class="btn" on:click="{() => {currentPage = 1;document.querySelector('#anchor').scrollIntoView({behavior: 'smooth'})}}">Back</button>
                <button class="btn" on:click="{() => {currentPage = 3;document.querySelector('#anchor').scrollIntoView({behavior: 'smooth'})}}">Next</button>
            </div>
        </div>

    {:else if currentPage === 3}
        <div class="box">
            <h2>Step 3: Decisions, decisions...</h2>
            <div class="section">
                <div><strong>Who should we send party prop boxes to?</strong></div>
                <p>We would like to know who needs an activity party box.
                    Each box contains homemade and eco-friendly activity gifts and party decorations.
                    Gifts will be age appropriate for your party.</p>
                <p>Each party box costs £{prices.box1.toFixed(2)} + P&P</p>
                <button class="btn btn-purple"
                        class:selected={boxBtns === 1}
                        on:click={()=>{setBoxes(1)}}
                >
                    Just {data.kidName ? data.kidName : "the party's superstar"}
                </button>
                <button class="btn btn-purple"
                        class:selected={boxBtns === 2}
                        on:click={()=>{setBoxes(2)}}
                >
                    Everybody attending
                </button>
                <button class="btn btn-purple"
                        class:selected={boxBtns === 0}
                        on:click={()=>{setBoxes(0)}}
                >
                    No boxes, just the party
                </button>
                <div>
                    <table class="container">
                        <tr>
                            <td style="padding-right: 12px;">{data.kidName ? data.kidName : "The party's superstar"}</td>
                            <td>
                                <button class="btn btn-purple" class:selected={data.kidBox} on:click={()=>{data.kidBox = true;boxBtns=-1;}}>Send box</button>
                                <button class="btn btn-purple" class:selected={!data.kidBox} on:click={()=>{data.kidBox = false;boxBtns=-1;}}>No box</button>
                            </td>
                        </tr>

                    {#each data.guests as guest, i}
                        <tr>
                            <td>{guest.name ? guest.name : `Guest ${i+1}`}</td>
                            <td>
                                <button class="btn btn-purple" class:selected={guest.box} on:click={()=>{guest.box = true;boxBtns=-1;}}>Send box</button>
                                <button class="btn btn-purple" class:selected={!guest.box} on:click={()=>{guest.box = false;boxBtns=-1;}}>No box</button>
                            </td>
                        </tr>
                    {/each}
                        <tr>
                            <td style="text-align: right;">
                                <strong>Total box cost:</strong>
                            </td>
                            <td>
                                <em>£{costs.boxes.toFixed(2)}</em>
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
            <!--div class="section">
                <div><strong>Would you like to upgrade to premium party boxes?</strong></div>
                <p>Our normal boxes contain top quality gifts and props for use during the party. However, we are able
                    to upgrade these boxes to a more bespoke package for an additional £9 per box.</p>
                <button class="btn"
                        style={"margin: 0 3px;" + (data.premium ? "background: var(--orange)" : "background: var(--purple)")}
                        on:click={()=>{data.premium = true}}
                >
                    Premium boxes
                </button>
                <button class="btn"
                        style={"margin: 0 3px;" + (!data.premium ? "background: var(--orange)" : "background: var(--purple)")}
                        on:click={()=>{data.premium = false}}
                >
                    Standard boxes
                </button>
            </div>
            <div class="section">
                <div><strong>Would you like a custom video to be sent in advance of the party?</strong></div>
                <p>It's often exciting to receive a 'teaser' video before the party. This 5 minute introduction will be
                    customised for {data.kidName ? data.kidName : "the party's superstar"}, and introduces them to the
                    characters, the concept, and their party box.</p>
                <button class="btn"
                        style={"margin: 0 3px;" + (data.introvid ? "background: var(--orange)" : "background: var(--purple)")}
                        on:click={()=>{data.introvid = true}}
                >
                    Yes
                </button>
                <button class="btn"
                        style={"margin: 0 3px;" + (!data.introvid ? "background: var(--orange)" : "background: var(--purple)")}
                        on:click={()=>{data.introvid = false}}
                >
                    No
                </button>
            </div-->

            <div class="button-bar">
                <button class="btn" on:click="{() => {currentPage = 2;document.querySelector('#anchor').scrollIntoView({behavior: 'smooth'})}}">Back</button>
                <button class="btn" on:click="{() => {currentPage = 4;document.querySelector('#anchor').scrollIntoView({behavior: 'smooth'})}}">Next</button>
                <!-- TODO Need error checking on the next button in case there's missing info in the form -->
            </div>

        </div>

    {:else}
        <div class="box" style="text-align: left !important;line-height: 1.8em;">
            <h2>Step 4: Summary</h2>
            <div class="receipt">
                <div style="margin: 0 0 12px;"><strong>Party for:</strong> {data.kidName ? data.kidName : "(anonymous)"}</div>
                <div style="margin: 0 0 12px;"><strong>Hosted by:</strong> {data.host}</div>
                <div style="margin: 0 0 12px;"><strong>Date:</strong> {data.dateChosen.toDateString()}</div>
                <div style="margin: 0 0 12px;"><strong>Time:</strong> {data.timeslot}</div>
                <div style="margin: 0 0 12px;"><strong>Guests:</strong>
                    <ul style="margin: 0">
                        {#each data.guests as guest, i}
                            <li>{guest.name ? guest.name : `Guest ${i+1}`}{#if guest.box}: (with party box sent){/if}</li>
                        {/each}
                    </ul>
                    <!--div style="margin: 0 0 12px;"><strong>Custom introduction video:</strong> {data.introvid ? "Yes" : "No"}</div>
                    <div style="margin: 0 0 12px;"><strong>Party box style:</strong> {data.premium ? "Premium" : "Standard"}</div>
                    <div style="margin: 0 0 12px;"><strong>Party boxes sent to: </strong>
                        {#if data.boxesTo === 0}
                            (None)
                        {:else if data.boxesTo === 1}
                            Just {data.kidName ? data.kidName : "the party's superstar"}
                        {:else if data.boxesTo === 2}
                            All attendees
                        {/if}
                    </div-->
                    <div style="margin: 0 0 12px;text-align: center;"><em>If any of these options are incorrect please click the "Back" below to change them.</em>
                    </div>
                </div>
                <p><strong>Invoice</strong></p>
                <table style="width:100%;">
                    <tr>
                        <td>
                            1 x 1 hour online party
                        </td>
                        <td>
                            £{(costs.party).toFixed(2)}
                        </td>
                    </tr>
                    <tr>
                        <td>
                            {boxCount} x party boxes
                        </td>
                        <td>
                            £{costs.boxes.toFixed(2)}
                        </td>
                    </tr>
                    <tr>
                        <td>
                            {boxCount} x box postage
                        </td>
                        <td>
                            £{costs.postage.toFixed(2)}
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <strong>Total</strong>
                        </td>
                        <td>
                            <em>£{total.toFixed(2)}</em>
                        </td>
                    </tr>
                </table>
            </div>

            <div class="button-bar">
                <button class="btn" on:click="{() => {currentPage = 3;document.querySelector('#anchor').scrollIntoView({behavior: 'smooth'})}}">Back</button>
                {#if spinner}
                    <div class="btn btn-purple spinny-button" on:click={pay}><img src="/img/810.gif" style="height:24px;width:24px;" alt="spinner"></div>
                    {:else}
                    <button class="btn btn-purple" on:click={pay}>Book now!</button>
                    {/if}
            </div>
        </div>

    {/if}

    <div class="vspacer">&nbsp;</div>


</div>


