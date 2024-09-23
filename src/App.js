import React, { useState, useEffect, useCallback, useRef } from 'react';
import TextField from '@mui/material/TextField';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { TimePicker } from '@mui/x-date-pickers/TimePicker';
import { styled } from '@mui/material/styles';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';
import * as Sentry from "@sentry/react";
import { BrowserTracing } from "@sentry/tracing";

function App() {
  const [isSending, setIsSending] = useState(false)
  const [switchStatus, setSwitchStatus] = useState(false)
  const [roomStatus, setRoomStatus] = useState(false)
  const [showSnooze, setShowSnooze] = useState(false)
  const [value, setValue] = React.useState(null);
  const [buttonText, setButtonText] = React.useState("Submit");
  const isMounted = useRef(true)
  const Android12Switch = styled(Switch)(({ theme }) => ({
    padding: 8,
    '& .MuiSwitch-track': {
      borderRadius: 22 / 2,
      '&:before, &:after': {
        content: '""',
        position: 'absolute',
        top: '50%',
        transform: 'translateY(-50%)',
        width: 16,
        height: 16,
      },
      '&:before': {
        backgroundImage: `url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24"><path fill="${encodeURIComponent(
          theme.palette.getContrastText(theme.palette.primary.main),
        )}" d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z"/></svg>')`,
        left: 12,
      },
      '&:after': {
        backgroundImage: `url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24"><path fill="${encodeURIComponent(
          theme.palette.getContrastText(theme.palette.primary.main),
        )}" d="M19,13H5V11H19V13Z" /></svg>')`,
        right: 12,
      },
    },
    '& .MuiSwitch-thumb': {
      boxShadow: 'none',
      width: 16,
      height: 16,
      margin: 2,
    },
  }));

  const calculateTimeLeft = (arg) => {

    const wakeUpTime = new Date()
    if (typeof arg === 'string' || arg instanceof String){
      wakeUpTime.setHours(arg.substring(16,18),arg.substring(19,21),arg.substring(22,24))
    }
    else{
      wakeUpTime.setTime(arg)
    }
    
    const difference = +wakeUpTime - +new Date();

    let timeLeft = {};

    if (difference > 0) {
      timeLeft = {
        hours: Math.floor(difference / (1000 * 60 * 60)),
        minutes: Math.floor((difference / 1000 / 60) % 60),
        seconds: Math.floor((difference / 1000) % 60),
      };
    }
    else{
      timeLeft = {
        hours: Math.floor(difference / (1000 * 60 * 60) + 24),
        minutes: Math.floor((difference / 1000 / 60) % 60 + 60),
        seconds: Math.floor((difference / 1000) % 60 + 60),
      };
    }

    return timeLeft;
  };

  const [timeLeft, setTimeLeft] = useState('00:00:00');

  useEffect(() => {
    fetch('/alarmstatus').then(res => res.json()).then(data => {
      if(data.status === 'true'){
        setIsSending(true);
      }
      if(data.room === 'true'){
        setSwitchStatus(true);
      }
      if(data.trigger === 'true'){
        setShowSnooze(true);
      }
    });

    return () => {
      isMounted.current = false
    }
  }, [])

  useEffect(() => {
    fetch('/getwakeuptime').then(res => res.json()).then(data => {
      if (data.time == "null"){
        setValue(null)
      }
      else{
        var setValueTime = "Sun Aug 28 2022 " + data.time + " GMT-0400 (Eastern Daylight Time)"
        setValue(setValueTime)
      }
    });
  }, [])
  
  useEffect(() => {
    if(!showSnooze){
      setTimeout(() => {
        setTimeLeft(calculateTimeLeft(value));
      }, 1000);
      if(isSending == true){
        if(timeLeft.hours){
          setButtonText("Wake Up in " + timeLeft.hours.toLocaleString('en-US', {minimumIntegerDigits: 2,useGrouping: false}) + ":" + timeLeft.minutes.toLocaleString('en-US', {minimumIntegerDigits: 2,useGrouping: false}) + ":" + timeLeft.seconds.toLocaleString('en-US', {minimumIntegerDigits: 2,useGrouping: false}))
        }
        if(!timeLeft.hours && timeLeft.minutes){
          setButtonText("Wake Up in 00:" + timeLeft.minutes.toLocaleString('en-US', {minimumIntegerDigits: 2,useGrouping: false}) + ":" + timeLeft.seconds.toLocaleString('en-US', {minimumIntegerDigits: 2,useGrouping: false}))
        }
        if(!timeLeft.hours && !timeLeft.minutes && timeLeft.seconds){
          setButtonText("Wake Up in 00:00:" + timeLeft.seconds.toLocaleString('en-US', {minimumIntegerDigits: 2,useGrouping: false}))
        }
        if(timeLeft.hours == 0 && timeLeft.minutes == 0 && timeLeft.seconds == 0){
          if(value != null){
            console.log(value)
            setShowSnooze(true)
            setButtonText("GET UP!!!")
          }
        }
      }
    }
  })

  const sendTimeRequest = useCallback(async () => {
    // don't send again while we are sending
    if (isSending) return
    // don't send dont send if value is null
    if (!value) return
    // update state
    setIsSending(true)
    // send the actual request
    await fetch('/setalarmclock', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({time: value})
    }).then(res => res.json()).then(data => {
      console.log(data);
    });

    // once the request is sent, update state again
    if (isMounted.current) // only update if we are still mounted
      setIsSending(false)
  }, [isSending,value]) // update the callback if the state changes

  const sendCancelRequest = useCallback(async () => {
    // don't send again while we are sending
    if (!isSending) return
    //hide snooze button when cancelled
    setShowSnooze(false)
    setButtonText("Submit")
    setIsSending(false)
    setValue(null)
    //GET to cancel current alarm and set to original state
    fetch('/alarmcancel').then(res => res.json()).then(data => {
    });

  }, [isSending])

  const sendSnoozeRequest = useCallback(async () => {
    // don't send again while we are sending
    if (!isSending) return

    setButtonText("Snoozed...")

    //GET to cancel current alarm and set new alarm 15 minutes later
    fetch('/alarmpause').then(res => res.json()).then(data => {
    });

  }, [isSending])

  const sendRoomToggleRequest = useCallback(async () => {
    if (showSnooze){
      //hide snooze button when cancelled
      setShowSnooze(false)
      setButtonText("Submit")
      setIsSending(false)
      setValue(null)
    }
    //send GET request to turn on/off the tv speakers and PC
    fetch('/roomcontrol').then(res => res.json()).then(data => {
      //fix for toggle not staying in correct position after press
      if (data.response === 'Room Status: On'){
        setSwitchStatus(true)
        console.log("switch on")
      }
      else{
        setSwitchStatus(false)
        console.log("switch off")
      }
    });
  }, [showSnooze])

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
    >
      <Grid container
            spacing={1}
            direction="column"
            alignItems="center"
            justifyContent="center"
            >
        <Grid item xs = {12}>
          <LocalizationProvider dateAdapter={AdapterDateFns}>
                <TimePicker
                  label="Wake Up Time: "
                  value={value}
                  disabled={isSending}
                  onChange={(newValue) => {
                    setValue(newValue);
                  }}
                  renderInput={(params) => <TextField {...params} />}
                />
          </LocalizationProvider>
        </Grid> 
        <Grid item xs = {12}>
          <Button variant="contained" disabled={isSending} onClick={sendTimeRequest}>{buttonText}</Button>  
          <Button variant="contained" disabled={!isSending} onClick={sendCancelRequest}>Cancel</Button>
          {showSnooze && <Button variant="contained" disabled={!isSending} onClick={sendSnoozeRequest}>Snooze</Button>}
        </Grid>
        <Grid item xs = {12}>
          <FormControlLabel
            control={<Android12Switch defaultChecked={switchStatus} onChange={sendRoomToggleRequest}/>}
            label="Room Switch"
          />
        </Grid>
      </Grid>        
    </Box>
  )
}


export default App;
