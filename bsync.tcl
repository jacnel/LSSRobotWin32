# Copyright (C)1998-1999 Khaldoun Shobaki <kal@shobaki.org>
# Copyright (C)1998-2002 Center for Spoken Language Understanding,
#                        OGI School of Science & Engineering,
#                        Oregon Health & Science University
#
# See the file "license.ogi" for information on usage and redistribution
# of this file, and for a DISCLAIMER OF ALL WARRANTIES.
#
# $Revision: 1.31 $
# --------------------------------------------------------------------------
# Tools for saving and reading synchronous audio/animation/+
# --------------------------------------------------------------------------
#
# <SABLE>Hello<SPEAKER NAME='abc'>ferrocaril</SPEAKER>world</SABLE>

package provide Bsync 1.0

# export only the published API to the package database
if {![string compare dummy [package unknown]]} {
 proc bsync {} {}
 proc sobPlay {} {}
 proc sobInfo {} {}
 return
}

package require SpeechView
package require Genrecog
package require Widgets
package require RemapLibrary

package require Rtcl
package require Misc
package require Wave
package require Audio
package require Face
package require TTS

#-----------------------------------------------------------------------
# Hacked from SpeechView, modified to use the face if available.
# 2000-05-10 Jacques@deVilliers.com
# yuck spit etc.
package require AudioIOWidget
auto_load PlayZoomed

#
# PlayZoomed  plays a zoomed region of the wave file; this region
# will be the wave window if "which_window" is the *map* window,
# or the highlighted region inside the wave window if "which_window"
# is the *wave* window

proc PlayZoomed {group which_type} {
 global Disp CurrGroup

 if {$group < 0} {set group $CurrGroup}
 if {$Disp(recording)} {StopRecording}
 set wave_window [FindWindowFromType "wave" $group]
 set map_window  [FindWindowFromType "map"  $group]
 set name        [FindNameFromType $which_type $group]
 if {[string compare $name "NULL_NAME"] != 0} {
  # if the name is not null, then it is either "wave" or "map"
  set begin  $Disp($group,$name,left)
  set end    $Disp($group,$name,right)
 } {
  # if the name is not a regular type, check if it is the name
  # of a label window. If it isn't a label window, return. 
  # Otherwise, set the begin and end points to active segment
  # boundaries
  set label_check [FindTypeFromWindow $which_type $group]
  if {[string compare $label_check "label"] != 0} {return 0}
  set segment [$which_type getactive]
  set begin   [lindex $segment 0]
  set end     [lindex $segment 1]
 }
 if {[info exists Disp($group,wave)]} {
  if {[catch {wave info $Disp($group,wave)}]} {
   tk_messageBox \
     -message "Program Error: wave was accidently nuked."
   return -1
  }
  if {$begin < 0 || $begin >= $end} {return -1}
  set subwav [wave chop  $Disp($group,wave) -begin $begin -end $end]
  set max    [lindex [lindex [wave info -max $subwav] 0] 0]
  
  # 99/01/29 kal@shobaki.org
  # added to avoid divide by zero with empty wave
  if {$max == 0} {set max 1}
  set scale  [expr double($Disp(max_wave_value))/double($max)]
  if {$max >= 0.001} {
   set scaled_wav [wave scale $subwav $scale]
  } {
   set scaled_wav [object clone $Disp($group,wave)]
  }
  StopPlayRecord

  # well, well, well...
  set pl {}
  foreach px [.bsync.labelG1N2.labelG1N2 get] {
   foreach {pb pe pv} $px break
   if {$pe>$end} break
   if {$pb>=$begin} {lappend pl [list [expr $pb-$begin] [expr $pe-$begin] $pv]}
  }
  if {[lsearch -exact {pc tc kc bc dc gc vc uc tSc dZc t\\\[c d\\\[c}\
    [lindex [lindex $pl end] 2]]>=0} {
   set pl [lrange $pl 0 [expr [llength $pl]-2]]
  }
  set wl {}
  foreach wx [.bsync.labelG1N1.labelG1N1 get] {
   foreach {wb we wv} $wx break
   if {$we>$end} break
   if {$wb>=$begin} {lappend wl [list [expr $wb-$begin] [expr $we-$begin] $wv]}
  }
  if {![llength $wl]} {set wl [list 0 [expr $end-$begin] {}]}
  set ll {}
  foreach lx [.bsync.labelG1N3.labelG1N3 get] {
   foreach {lb le lv} $lx break
   if {$lb>$end} break
   if {$le<=$begin} continue
   if {$lb<=$begin} {
    lappend ll [list 0 [expr $le-$begin] $lv]
   } {
    lappend ll [list [expr $lb-$begin] [expr $le-$begin] $lv]
   }
  }
  
  if {!$::bsync::nobaldi && [llength $pl]} {
   set s(palign,1) $pl
   set s(walign,1) $wl
   set s(lalign,1) $ll
   set s(language,1) [bsync::lalign->language $pl $ll]
   array set ::S [array get s]
   #$::bsync::bface setLanguage $::bsync::tts(language)
   $::bsync::bface <-Transcription [array get s]
   $::bsync::bface <-Wave $scaled_wav
  } {
   play <-Wave $scaled_wav
  }
  if {[string compare $wave_window "NULL_WINDOW"] != 0} {
   $wave_window  sync start -from $begin -to $end
  }
  if {[string compare $map_window "NULL_WINDOW"] != 0} {
   $map_window   sync start -from $begin -to $end
  }
  nuke $subwav $scaled_wav
 }
 return 0
}


namespace eval ::bsync {
 namespace export bsync
 namespace export sobPlay
 namespace export sobMake
 namespace export sobInfo

 variable sobdesc "SOB player"
 variable bsyncdesc "Baldi Lipsync Tool"
 variable Recogniser

 array set Recogniser {
  English adult_english_16khz_1.ob
  Spanish adult_spanish_8khz_0.ob
 }

 proc alignLabels {in out} {
  set n {}
  foreach o $out {
   foreach {os oe} $o break
   set s 1e9; set e 1e9
   foreach i $in {
    foreach {is ie} $i break
    if {[set ds [expr abs($os-$is)]]<$s} {set s $ds; set ns $is}
    if {[set de [expr abs($oe-$ie)]]<$e} {set e $de; set ne $ie}
   }
   lappend n [concat [list $ns] [list $ne] [lrange $o 2 end]]
  }
  return $n
 }

 # will preserve only lrange 0 2 of label entries
 # gaps between labels are filled in
 proc coalesceLabels labels {
  if {[llength $labels]<2} {return $labels}
  foreach {os oe ol} [lindex $labels 0] break
  foreach l [lrange $labels 1 end] {
   foreach {ls le ll} $l break
   if {[string compare $ol $ll]} {
    lappend n [list $os $ls $ol]
    foreach {os oe ol} $l break
   }
  }
  lappend n [list $os $le $ol]
  return $n
 }

 proc language->lalign {palign language} {
  set n {}
  foreach p $palign l $language {
   if {[string match s* $l] || [string match S* $l]} {
    set l Spanish
   } {
    set l English
   }
   lappend n [list [lindex $p 0] [lindex $p 1] $l]
  }
  return [coalesceLabels $n]
 }

 proc lalign->language {palign lalign} {
  if {![llength $lalign]} {return {}}
  set n {}
  set lalign [alignLabels $palign $lalign]
  set li 0
  foreach {ls le ll} [lindex $lalign $li] break
  set ls [expr round($ls)]
  set le [expr round($le)]
  foreach p $palign {
   foreach {ps pe} $p break
   set ps [expr round($ps)]
   set pe [expr round($pe)]
   if {$pe<=$le} {lappend n $ll} {
    while {1} {
     incr li
     foreach {ls le ll} [lindex $lalign $li] break
     if {$ps<=$le || $li>=[llength $lalign]} break
    }
    lappend n $ll
   }
  }
  return $n
 }

 proc fixLabels {} {
  set p [.bsync.labelG1N2.labelG1N2 get]
  # align word labels with phonemes
  OpenLabel list [alignLabels $p [.bsync.labelG1N1.labelG1N1 get]] 1 labelG1N1
  # clean up and align language labels with phonemes
  set ll {}
  foreach lx [.bsync.labelG1N3.labelG1N3 get] {
   foreach {ls le lv} $lx break
   if {[string match s* $lv] || [string match S* $lv]} {
    set lv Spanish
   } {
    set lv English
   }
   lappend ll [list $ls $le $lv]
  }
  # make sure that the first language label starts at 0ms and that the
  # last label extends to the end of the wave
  set ll [alignLabels $p [coalesceLabels $ll]]
  puts "0 ll=$ll"
  set ll [lreplace $ll 0 0 [concat 0.00 [lrange [lindex $ll 0] 1 2]]]
  set e [lindex $ll end]
  set ll [lreplace $ll end end [list [lindex $e 0]\
    [expr int([wave info $::Disp(1,wave) -time])] [lindex $e 2]]]
  puts "1 ll=$ll"
  OpenLabel list $ll 1 labelG1N3
 }

 proc getElements {entry startVar endVar valueVar} {
  upvar $startVar start
  upvar $endVar end
  upvar $valueVar value
  foreach {start end value} $entry break
  set start [expr round($start)]
  set end [expr round($end)]
  return
 }

 proc getWordsAndGrammar {walign palign start end wordsVar grammarVar} {
  upvar $wordsVar words
  upvar $grammarVar grammar
  set sep {[*sil%%] [*any%%] [*sil%%]}
  #set sep {[*sil%%]}
  set sep {{[*any%%] [*sil%%]}}
  set words {{"*sil" {.pau}} {"*any" {.garbage}}}
  set grammar "$sep "
  set pi 0
  foreach wx $walign {
   getElements $wx ws we wv
   if {$ws<$start} continue
   if {$we>$end} break
   set wp ""
   for {} {$pi<[llength $palign]} {incr pi} {
    getElements [lindex $palign $pi] ps pe pv
    if {$pe>$we} break
    if {$pe>$we ||\
      ($pe==$we && [string length $wp] && [string match .pau $pv])} break
    if {$ps>=$ws} {append wp "$pv "}
   }
   lappend words [list $wv [string trim $wp]]
   append grammar "$wv $sep "
  }
  set grammar [list [list "force" [format {$grammar = %s;} $grammar]]]
  return
 }

 # Takes wave and alignments from the widget structure, then realigns
 # the phonemes with an appropriate recogniser
 proc realign {} {
  variable Recog
  variable Search
  variable Recogniser
  fixLabels
  set wl [.bsync.labelG1N1.labelG1N1 get]
  if {![llength $wl]} {
   if {[string length [string trim [.bsync.frame.te.text get 1.0 end]]]} {
    text->labels
    set wl [.bsync.labelG1N1.labelG1N1 get]
   } {
    tk_messageBox -type ok -icon error -title "BaldiSync" -message\
      "Alignment requires a text string.\
      \nType the recording transcription into the text box."
    return
   }
  }
  if {[wave info $::Disp(1,wave) -ave]<1.0} {
   tk_messageBox -type ok -icon error -title "BaldiSync" -message\
     "Alignment requires a recording.\
     \nRecord speech by pressing the red record button."
   return
  }
  set pl [.bsync.labelG1N2.labelG1N2 get]
  set ll [.bsync.labelG1N3.labelG1N3 get]

  foreach lx $ll {
   getElements $lx ls le lv
   getWordsAndGrammar $wl $pl $ls $le words grammar
   set wave [wave chop $::Disp(1,wave) -begin $ls -end $le]
   puts stderr "language=$lv"
   puts stderr " words=$words\n grammar=$grammar"
   puts stderr " wave info: [wave info $wave]"
   puts stderr ""
   set info(active) 1.0
   set info(garbage) {30 30}
   set info(recog) $Recogniser($lv)
   genrecog initialize Recog info
   array set ri [genrecog info $info(recog)]
   if {int([wave info -rate $wave])!=$ri(infoRate)} {
    set wn [wave sampleconvert $wave $ri(infoRate)]
    nuke $wave; set wave $wn
   }
   genrecog grammar Recog Search $grammar $words usephonemebt
   genrecog pipe Recog Search $wave
   set res [genrecog result Recog Search]
   genrecog nuke Search Recog
   nuke $wave
   if {[string match Spanish $lv]} {
    # gack
    array set es $res
    regsub -all {r\(} $es(palign,1) {r\\\\(} es(palign,1)
    regsub -all {d\[} $es(palign,1) {d\\[} es(palign,1)
    regsub -all {t\[} $es(palign,1) {t\\[} es(palign,1)
    set res [array get es]
   }
   array set r $res
   foreach px $r(palign,1) {
    foreach {ps pe pv} $px break
    lappend R(palign,1) [list [expr $ls+$ps] [expr $ls+$pe] $pv]
    lappend R(language,1) $lv
   }
   foreach wx $r(walign,1) {
    foreach {ws we wv} $wx break
    lappend R(walign,1) [list [expr $ls+$ws] [expr $ls+$we] $wv]
   }
  }
  set R(lalign,1) [language->lalign $R(palign,1) $R(language,1)]
  OpenLabel list $R(walign,1) 1 labelG1N1
  OpenLabel list $R(palign,1) 1 labelG1N2
  OpenLabel list $R(lalign,1) 1 labelG1N3
  return [array get R]
 }
 
 proc playSync {} {
  global Disp
  variable sync
  variable bface
  variable baudio
  variable nobaldi
  set sync(walign,1) [.bsync.labelG1N1.labelG1N1 get]
  set sync(palign,1) [.bsync.labelG1N2.labelG1N2 get]
  set sync(wave) $Disp(1,wave)
  set sync(word,1) [string trim [.bsync.frame.te.text get 1.0 end]]
  set sync(lalign,1) [.bsync.labelG1N3.labelG1N3 get]
  set sync(language,1) [lalign->language $sync(palign,1) $sync(lalign,1)]

  if {![wave info $sync(wave) -ave]} {bell;return}
  if {[string match {} $sync(palign,1)]} {bell;return}
  if {$nobaldi} {
   $baudio <-Wave [scaleWave $sync(wave)]
   $baudio sync
  } {
   #$bface setLanguage $::bsync::tts(language)
   $bface <-Transcription [array get sync]
   $bface <-Wave [::bsync::scaleWave $sync(wave)]
   $bface <-Event __FACE_SYNC__
   $baudio waitfor __FACE_SYNC__
  }
 }

 proc scaleWave {w} {
  set maxV 32000
  set max [lindex [lindex [wave info -max $w] 0] 0]
  if {$max >= 0.001} {
   set sc [expr double($maxV)/double($max)]
   set s [wave scale $w $sc]
  } {
   set s [object clone $w]
  }
  return $s
 }

 
 proc setTTSLanguage args {
  variable tts
  variable btts
  if {[info exists tts(prevLanguage)] &&\
    [string match $tts(prevLanguage) $tts(language)]} return
  switch -- $tts(language) {
   English {$btts setVoice mwm}
   Spanish {$btts setVoice abc}
  }
  updateDisplay [list wave.0 [wave zero 1000]\
    phoneLabel.0 {} wordLabel.0 {} text.0 {} langLabel.0 {}]
  set tts(prevLanguage) $tts(language)
 }

 proc text->tts {} {
  variable tts
  variable btts
  set text [string trim [.bsync.frame.te.text get 1.0 end]]
  if {[string match {} $text]} return
  foreach {wave transcription} [$btts tts $text] break
  array set tts $transcription
  array set vi [$btts voiceInfo]
  set tts(text) $text
  set tts(wave) $wave
  # 2001-04-29 - temporary backwards compatibility with Festival 1.3.1
  #
  if {![info exists tts(language,1)]} {
   set tts(language,1) {}
   array set l [$btts voiceInfo]
   foreach p $tts(palign,1) {lappend tts(language,1) $l(language)}
  }
   
  set tts(lalign,1) [language->lalign $tts(palign,1) $tts(language,1)]
  return [list wave.0 $wave\
    wordLabel.0 $tts(walign,1) phoneLabel.0 $tts(palign,1)\
    langLabel.0 $tts(lalign,1) text.0 $text language.0 $vi(language)]
 }

 proc text->labels {} {
  if {![llength [set r [text->tts]]]} return
  array set t $r
  set cs [wave info -time $t(wave.0)]
  nuke $t(wave.0)
  set t(wave.0) $::Disp(1,wave)
  set ns [wave info -time $t(wave.0)]
  # adjust timings to match current waveform
  set d [expr {double($ns)/$cs}]
  foreach i {langLabel.0 phoneLabel.0 wordLabel.0} {
   for {set j 0} {$j<[llength $t($i)]} {incr j} {
    set a [lindex $t($i) $j]
    set a [lreplace $a 0 0 [expr {[lindex $a 0]*$d}]]
    set a [lreplace $a 1 1 [expr {[lindex $a 1]*$d}]]
    set t($i) [lreplace $t($i) $j $j $a]
   }
  }
  updateDisplay [array get t]
 }

 proc syncTTS {} {
  if {![llength [set r [text->tts]]]} return
  updateDisplay $r
 }

 proc DEADBEEF:syncRec {} {
  global Disp
  variable align
  set r [string trim [.bsync.frame.te.text get 1.0 end]]
  if {![wave info $Disp(1,wave) -ave]} return
  if {[string match {} $r]} return
  alignWave align $Disp(1,wave) $r
  set b {};foreach a $align(walign,1) {lappend b [lrange $a 0 2]}
  set align(walign,1) $b
  set b {};foreach a $align(palign,1) {lappend b [lrange $a 0 2]}
  set align(palign,1) $b
  set align(lalign,1) [list [list 0 [wave info $Disp(1,wave) -time] English]]
  OpenLabel list $align(walign,1) 1 labelG1N1
  OpenLabel list $align(palign,1) 1 labelG1N2
  OpenLabel list $align(lalign,1) 1 labelG1N3
  fixLabels
 }

 proc checkDisplay {} {
  global Disp
  set a 0; set b 0; set c 0
  set foo ""; set wrd ""; set phn ""
  catch {set wav [wave info -max $Disp(1,wave)]}
  catch {set wrd [.bsync.labelG1N1.labelG1N1 get]}
  catch {set phn [.bsync.labelG1N2.labelG1N2 get]}
  if {$wav != "{0 0 0.0}"} {set a 1}  
  if {$wrd != ""} {set b 1}
  if {$phn != ""} {set c 1}
  return [list $a $b $c]
 }

 proc pickWav {{mode "r"} {dir ""}} {
  if {[string compare $mode "r"]} {
   set cmd [list tk_getSaveFile -title "Export wave..."]
  } {
   set cmd [list tk_getOpenFile -title "Import wave..."]
  }
  lappend cmd -filetypes {{wav {.wav}}} -initialdir $dir -defaultextension .wav
  if {[winfo exists .bsync]} {lappend cmd -parent .bsync}
  return [eval $cmd]
 }

 proc writeWav {name} {
  if {![llength $name]} return
  global Disp
  foreach {w r p} [checkDisplay] break
  if {[llength $w]} {wave write $Disp(1,wave) "$name"} {beep;return}
 }

 proc loadWav {name} {
  if {![string match $name ""]} {
   set wav [wave read "$name"]
   updateDisplay [list wave.0 $wav\
     phoneLabel.0 {} wordLabel.0 {} text.0 {} langLabel.0 {}]
  } {
   return
  }
 }

 proc pickSob {{mode "r"} {dir ""} {n ""}} {
  if {[string compare $mode "r"]} {
   set cmd [list tk_getSaveFile -title "Save sob..."]
  } {
   set cmd [list tk_getOpenFile -title "Load sob..."]
  }
  lappend cmd -filetypes {{sob {.sob}}} -initialdir $dir\
    -initialfile $n -defaultextension .sob
  if {[winfo exists .bsync]} {lappend cmd -parent .bsync}
  return [eval $cmd]
 }

 proc writeSob {name {fData {}}} {
  if {![llength $name]} return
  global Disp
  variable btts
  if {[llength $fData] == 0} {
   foreach {w r p} [checkDisplay] break
   set wlabel [.bsync.labelG1N1.labelG1N1 get]
   puts stderr $wlabel
   set plabel [.bsync.labelG1N2.labelG1N2 get]
   puts stderr $plabel
   set llabel [.bsync.labelG1N3.labelG1N3 get]
   puts stderr $llabel
   set t [.bsync.frame.te.text get 1.0 end]
   puts stderr $t
   set a [raw create -value $wlabel]
   set b [raw create -value $plabel]
   set c [raw create -value [string trim $t]]
   array set vi [$btts voiceInfo]
   set d [raw create -value $vi(language)]
   set e [raw create -value $llabel]
   set fData [list wave.0 $Disp(1,wave) wordLabel.0 $a phoneLabel.0 $b\
     text.0 $c language.0 $d langLabel.0 $e]
  }
  if {[file isfile $name]} {file delete -force $name}
  set f [obfile open "$name" w]
  foreach {x z} $fData {
    obfile write $f $x $z
  }

  catch {obfile close $f}
  if {![llength $fData]} {nuke $a $b $c $d $e}
  return 1
 }

 proc loadSob {name} {
  set fStat [checkSob $name v]
  if {[llength $fStat] == 0} return
  updateDisplay $fStat
 }

 proc checkSob {name {mode s}} {
  set infoList {}
  if {![file isfile $name]} {return}
  set f [obfile open "$name" r]
  set l [obfile fields $f]
  if {[string match $mode "s"]} {
   set valid [list wave.0 wordLabel.0 phoneLabel.0 text.0]
   foreach field $valid {
    if {[lsearch -exact $l $field] == -1} {obfile close $f; return}
   }
   obfile close $f
   return 1
  } {
   set rList {}
   foreach field $l {
    array set a [obfile info $f $field]
    lappend rList $field
    switch -exact -- $a(container) {
     "raw"  {lappend rList [raw set [set r [obfile read $f $field]]]; nuke $r}
     "wave" {lappend rList [obfile read $f $field]}
    }
   }
   obfile close $f
   # backwards compatibility, 2000-02-23 Jacques@deVilliers.com4
list {
 if {[lsearch -exact $l language.0]==-1} {
    lappend rList language.0 English
    lappend rList language_set.0 0
   } {
    lappend rList language_set.0 1
   }
  }
   array set R $rList
   if {[info exists R(language.0)]} {
    set R(language_set.0) 1
   } {
    set R(language_set.0) 1
    set R(language.0) English
   }
   if {![info exists R(langLabel.0)]} {
    # language label doesn't exist - build one from language.0 and phoneLabel.0
    set R(langLabel.0) [list [list\
      [lindex [lindex $R(phoneLabel.0) 0] 0]\
      [lindex [lindex $R(phoneLabel.0) end] 1]\
      $R(language.0)]]
   }
   return [array get R]
   return $rList
  }
 }

 proc updateDisplay {foo} {
  global Disp
  array set n $foo
  if {[info exists n(language.0)] &&\
    [string compare $::bsync::tts(language) $n(language.0)]} {
   set ::bsync::tts(language) $n(language.0)
  }
  .bsync.frame.te.text delete 1.0 end
  .bsync.frame.te.text insert 1.0 $n(text.0)
  set crud $Disp(1,wave)
  set Disp(1,wave) [::bsync::scaleWave $n(wave.0)]
  nuke $crud
  UpdateWaveInfo 1 ""
  DisplayAllWaveData 1
  OpenLabel list $n(wordLabel.0) 1 labelG1N1
  OpenLabel list $n(phoneLabel.0) 1 labelG1N2
  OpenLabel list $n(langLabel.0) 1 labelG1N3
  fixLabels
 }

 proc busyButton {command button} {
  set t [$button cget -text]
  $button configure -relief sunken -state disabled
  update idletasks
  uplevel $command
  $button configure -relief raised -state normal
  update idletasks
 }
 
 #procedure added by [cjg] and [clg] 6/10/2014
 #Text to speech and visual play back
 proc enterToSubmit {} {
	
	::bsync::syncTTS
	::bsync::playSync
	
	#clears text to wait for next input, old audio file still exists
	.bsync.frame.te.text delete 1.0 end

 }
 
 
 # Interface Setup
 #---------------------------------------------------------------------

 proc bsync {args} {
  global env
  variable f
  variable g
  variable textVar
  variable tts
  variable align
  variable bsyncdesc

  variable btts
  variable bface
  variable baudio
  variable inh
  variable nobaldi
  variable save_baudio
  variable save_btts
  variable save_bface

  set btts  ""
  set bface ""
  set baudio ""
  set filename ""
  set nobaldi 0

  set tts(text) ""
  wm withdraw .
  toplevel [set w .bsync]
  wm withdraw $w
  wm title $w "bsync - Baldi with natural speech"

  sview [list -Wo "[wave zero 1000];noruler" \
    -S -Ll  {} -Ll {} -Ll {} -label edge -sidebar -notoolbar] .bsync

  $w.mbar.help delete 0 end
  $w.mbar.file delete 0 end
  #  $w.mbar.options delete 2; # Leads to a core dump!  Ask not why...
  $w.mbar.options entryconfigure 0 -label "Sampling Rate"
  $w.mbar.options entryconfigure 1 -label "Scrolling"
  $w.mbar.options.samplingrate entryconfigure 0 -label " 8000 hz"
  $w.mbar.options.samplingrate entryconfigure 1 -label "16000 hz"
  $w.mbar.options.samplingrate entryconfigure 2 -label "11025 hz"
  $w.mbar.options.samplingrate entryconfigure 3 -label "22050 hz"
  $w.mbar.options.samplingrate entryconfigure 4 -label "44100 hz"
 
  $w.mbar.help add command -label "Baldi Sync Manual"\
   -command {::sys::showURL docs/2.0/apps/baldisync/index.html}
  $w.mbar.help add command -label "About..." -command "about_bsync up"
  set fMenu $w.mbar.file

  $fMenu add command -label "Load Sob..." \
    -command {::bsync::loadSob [::bsync::pickSob]}
  $fMenu add command -label "Save Sob..." \
    -command {::bsync::writeSob [::bsync::pickSob w]}
  $fMenu add separator
  $fMenu add command -label "Import Wav..." -command {::bsync::loadWav [::bsync::pickWav]}
  $fMenu add command -label "Export Wav..." -command {::bsync::writeWav [::bsync::pickWav w]}
  $fMenu add separator
  $fMenu add command -label "Show Console" -command "console show"
  $fMenu add separator
  $fMenu add command -label "Exit" -command {destroy .bsync}
  
  $w.frame configure -relief flat
  destroy $w.frame.val_frame
  
  foreach h {labelG1N1 labelG1N2 labelG1N3 waveG1 mapG1 specG1N1 scrollG1} {
   destroy $w.$h.bframe
   destroy $w.$h.selframe
   $w.$h configure -relief flat
   pack $w.$h -expand 0 -fill x

   foreach b {Button-3 Control-Key-s Alt-Key-o Alt-Key-a Alt-Key-l Alt-Ket-s} {
    catch {bind $w.$h.$h <$b> {}}
   }
  }

  label $w.frame.info -textvariable Disp(xy) -height 5 \
    -wraplength 120 -width 25 -justify left -anchor n

  set cf $w.frame.controls
  foreach a {blank0 playall playmap playhigh record stop} {
   pack forget $cf.$a
  }
  pack forget $cf
  pack forget $w.frame.values.xy
  pack forget $w.frame.values

  frame $cf.f
  button $cf.f.r -text "Align" -pady 0 -width 10\
    -command [list ::bsync::busyButton ::bsync::realign $cf.f.r]
  button $cf.f.t -text "TTS" -pady 0 -width 10\
    -command [list ::bsync::busyButton ::bsync::syncTTS $cf.f.t]
  #button $cf.f.a -text "Animate" -pady 0 -width 10 -command {::bsync::playSync}
  button $cf.f.l -text "Labels" -pady 0 -width 10\
    -command [list ::bsync::busyButton ::bsync::text->labels $cf.f.l]

  StickyNote attach $cf.f.r "Aligns phonetic labels with the audio sample"
  StickyNote attach $cf.f.l "Generates phonetic labels from text"
  StickyNote attach $cf.f.t "Generates audio sample and phonetic labels\
    \nfrom text using the Text-To-Speech engine."
  combobox $cf.f.language -textvariable ::bsync::tts(language)\
    -editable 0 -width 7 -value English
  $cf.f.language list insert end English Spanish
  $cf.f.language configure -command ::bsync::setTTSLanguage

  grid $cf.f.t x $cf.f.language -sticky ew
  grid $cf.f.l x $cf.f.r        -sticky ew -row 2
  #grid $cf.f.r x $cf.f.t
  grid columnconfigure $cf.f 1 -minsize 5
  grid rowconfigure $cf.f 1 -minsize 5
  $cf.playall configure -command {::bsync::playSync}

  grid x $cf.record x $cf.stop x $cf.playall x $cf.playmap x $cf.playhigh -sticky new -row 1
  grid x $cf.f      -   -      -    -        -    -           -      -       -sticky new -row 3
  grid rowconfigure $cf 2 -minsize 5
  grid columnconfigure $cf {0 2 4 6 8} -minsize 5

  frame $w.frame.te
  label $w.frame.te.l -text "Text to align with:"
  scrollbar $w.frame.te.y -command "$w.frame.te.text yview" -orient vertical
  text $w.frame.te.text -width 40 -height 4 -wrap word \
    -yscrollcommand "$w.frame.te.y set"

  pack $w.frame.te.l -side top -anchor w
  pack $w.frame.te.text -side left -fill both -expand 1
  pack $w.frame.te.y  -side right -fill y
  
  pack $w.frame -fill both -expand 1 -padx 5 -pady 5
  grid $w.frame.te -sticky news -row 0 -col 0
  grid $cf -sticky nsw -row 0 -col 1 -padx 5 -pady 5
  grid columnconfigure $w.frame 0 -weight 1
  grid rowconfigure $w.frame 0 -weight 1

  update idletasks
  wm geometry $w 540x[winfo reqheight $w]
  wm minsize $w 540 [winfo reqheight $w]

  set align(waveinfo) {}
  set align(text) {null}
  set tts(wave) {}
  set tts(text) {}

  for {set i 0}  {[llength $args] >= $i} {incr i} {
   set option [lindex $args $i]
   switch -regexp -- $option {
    {^-file}   { incr i; set filename [lindex $args $i] }
    {^-face}   { incr i; set bface [lindex $args $i] }
    {^-tts}    { incr i; set btts [lindex $args $i] }
    {^-audio}  { incr i; set baudio [lindex $args $i] }
    {^-nobaldi} {set nobaldi 1}
   }
  }

  set inh {}
  if {[string match "" $baudio] || ![llength [info commands $baudio]] || ![$baudio isAttached]} {
   set baudio b___audio; Audio create $baudio $bsyncdesc; lappend inh $baudio
  } {
   set save_baudio [$baudio list-> Event]
  }
  if {[string match "" $btts] || ![llength [info commands $btts]]} {
   set btts b___tts; TTS create $btts $bsyncdesc; lappend inh $btts
  } {
   set save_btts [$btts list-> Event]
  }

  if {$nobaldi} {
   .bsync.frame.controls.f.a configure -state disabled
  } {
   if {[string match "" $bface] || ![llength [info commands $bface]]} {
    set bface b___face; Face create $bface $bsyncdesc; lappend inh $bface
   }
   set save_bface [$bface list-> Event]
   $bface list-> Wave [list [list $baudio <-Wave]]
   $bface list-> Event [list [list $baudio <-Event]]
   $baudio list-> Event [list [list $bface <-SyncEvent]]
  }

  bind .bsync <Destroy> {if {"%W" == ".bsync"} {::bsync::exitBsync}}

  if {[llength [info command ::bsync::mySetFocus]]} {
   rename ::SetFocus {}
   rename ::bsync::mySetFocus ::SetFocus
  }
  wm deiconify .bsync
  update idletasks

  Splash create about_bsync
  about_bsync subtitle "baldi sync"
  about_bsync click

  if {![string match "" $filename]} {
   update
   # needed or the Lyre widgets will core dump due to uninitialised
   # access.  Sigh.  These widgets are in serious need of a rewrite
   #  - 2000-07-24 Jacques@deVilliers.com
   ::bsync::loadSob [file join $filename]
  }
  
  #[cjg] [clg] bind Return to enterToSubmit
  bind .bsync <Return> {::bsync::enterToSubmit}
  
 }

 proc exitBsync {} {
  variable inh
  variable bface
  variable btts
  variable baudio
  variable nobaldi
  variable save_baudio
  variable save_btts
  variable save_bface
  catch {$bface list-> Event $save_bface}
  catch {$baudio list-> Event $save_baudio}
  catch {$btts list-> Event $save_btts}
  foreach z $inh {$z list-> Event {}}
  foreach a $inh {catch {rename $a {}}}
  foreach a {save_baudio save_btts save_bface inh bface btts baudio nobaldi} {
   catch {unset $a}
  }
 }

 proc mySetFocus {group type} {
  global Disp OldFocusWindow CurrGroup
  
  if {[string compare $type "wave"] == 0} {
   set focus_window [FindWindowFromType $type $group]
   set focus_name   [FindNameFromType   $type $group]
  } else {
   set focus_window $type
   set focus_name   [FindNameFromWindow $focus_window $group]
  }
  if {[string compare $focus_window "NULL_WINDOW"] == 0 || \
    [string compare $focus_name   "NULL_NAME"] == 0} {
   return 0
  }
  
  set new_focus_window {}
  focus $focus_window
  set OldFocusWindow $new_focus_window
  set CurrGroup $group
  
  return 0
 }
       
 proc sobPlay {args} {
  variable sobdesc

  set bface ""
  set baudio ""
  set nobaldi 0
  set inh {}

  for {set i 0}  {[llength $args] >= $i} {incr i} {
   set option [lindex $args $i]
   switch -regexp -- $option {
    {^-file}      { incr i; set filename [lindex $args $i] }
    {^-face}      { incr i; set bface [lindex $args $i] }
    {^-audio}     { incr i; set baudio [lindex $args $i] }
    {^-nobaldi}   { set nobaldi 1}
   }
  }

  set fStat [checkSob $filename v]
  if {[llength $fStat] == 0} return
  array set a $fStat
  set sync(walign,1) $a(wordLabel.0)
  set sync(palign,1) $a(phoneLabel.0)
  set sync(word,1) $a(text.0)
  set sync(lalign,1) $a(langLabel.0)
  set sync(language,1) [lalign->language $sync(palign,1) $sync(lalign,1)]
  if {![wave info $a(wave.0) -ave]} return
  if {[string match {} $sync(palign,1)]} return

  if {[string match "" $baudio] || ![llength [info commands $baudio]] || ![$baudio isAttached]} {
   set baudio b___audio; Audio create $baudio $sobdesc; lappend inh $baudio
  } {
   set sbaudio [$baudio list-> Event]
  }

  if {$nobaldi} {
   $baudio <-Wave $a(wave.0)
   $baudio sync
  } {
   if {[string match "" $bface] || ![llength [info commands $bface]]} {
    set bface b___face; Face create $bface $sobdesc; lappend inh $bface
   } {
    set sbface [$bface list-> Event]
   }
   #$bface setLanguage $a(language.0)
   $bface list-> Wave [list [list $baudio <-Wave]]
   $bface list-> Event [list [list $baudio <-Event]]
   $baudio list-> Event [list [list $bface <-SyncEvent]]
   $bface <-Transcription [array get sync]
   $bface <-Wave $a(wave.0)
   $bface <-Event __FACE_SYNC__
   catch {$baudio waitfor __FACE_SYNC__}
  }
  nuke $a(wave.0)
  catch {$bface list-> Event $sbface}
  catch {$baudio list-> Event $sbaudio}
  foreach z $inh {$z list-> Event {}}
  foreach z $inh {catch {rename $z {}}}
  unset a
  unset inh
  unset sync
  return 1
 }

 proc sobInfo {file} {
  if {![llength [checkSob $file]]} {
   return
  } {
   file stat $file fStat
   set ff {}
   set a [obfile open $file r]
   foreach f [obfile fields $a] {
    lappend ff $f
    array set i [obfile info $a $f]
    set info($f,type) $i(container)
    set info($f,size) $i(length)
   }
   set text [raw set [set r [obfile read $a text.0]]]; nuke $r
   if {[info exists info(language.0,type)]} {
    set language [raw set [set r [obfile read $a language.0]]]; nuke $r
   } {
    set language English
   }
   obfile close $a
   unset i
  }

  set w .[join [timestamp] ""]
  wm withdraw .
  wm withdraw [toplevel $w]

  set b [notebook $w.b]
  button $w.ok -text "Ok" -width 10 -command "destroy $w"
  grid x $b -sticky news -row 1
  grid x $w.ok -sticky e -row 3
  grid columnconfigure $w 1 -weight 1
  grid columnconfigure $w 0 -minsize 5
  grid columnconfigure $w 2 -minsize 5
  grid rowconfigure $w 1 -weight 1
  grid rowconfigure $w 0 -minsize 5
  grid rowconfigure $w 2 -minsize 10
  grid rowconfigure $w 4 -minsize 5

  set c [$b addpage gen -text "General"]  
  set d [$b addpage det -text "Details"]

  set i 1
  set burple [list "Filename: " [file tail $file] \
                    "Size (bytes): "     $fStat(size) \
		    "Last Mod: " [clock format $fStat(mtime) -format %c] \
		    "Language: " $language\
		    ]

  foreach {a b} $burple {
   frame $c.f$i -relief sunken -bg yellow
   label $c.f$i.nl -text $a -width 10 -anchor e
   label $c.f$i.n  -text $b
   grid $c.f$i.nl $c.f$i.n -sticky w
   grid $c.f$i.nl -sticky e
   grid x $c.f$i -sticky w -padx 5 -row $i
   incr i
  }


  set q [titledFrame $c.b -text "Text"]
  grid x $c.b -sticky news -row $i
  grid columnconfigure $c 0 -minsize 5
  grid rowconfigure $c 0 -minsize 5
  grid rowconfigure $c [expr $i+1] -minsize 5
  grid columnconfigure $c 1 -weight 1
  grid columnconfigure $c 2 -minsize 5
  grid rowconfigure $c $i -weight 1

  text $q.t -width 10 -height 2 -yscrollcommand "$q.s set"  -wrap word
  scrollbar $q.s -command "$q.t yview" 
  grid x $q.t $q.s -sticky news -row 1
  grid columnconfigure $q 0 -minsize 5
  grid columnconfigure $q 3 -minsize 5
  grid rowconfigure $q 0 -minsize 5
  grid rowconfigure $q 2 -minsize 5
  grid columnconfigure $q 1 -weight 1
  grid rowconfigure $q 1 -weight 1

  $q.t insert 1.0 "$text"
  $q.t configure  -state disabled

  scframe $d.f
  set a [$d.f frame]
  frame $d.v
  label $d.v.l1 -text "Field Name" -width 12 -anchor w -fg blue
  label $d.v.l2 -text "Type" -width 5 -anchor w -fg blue
  label $d.v.l3 -text "Size (bytes)" -width 10 -anchor w -fg blue

  grid x $d.v.l1 x $d.v.l2 x $d.v.l3 -sticky w

  grid x $d.v -sticky w
  grid x $d.f -sticky news
  grid rowconfigure $d 1 -weight 1
  grid rowconfigure $d 2 -minsize 5
  grid columnconfigure $d 0 -minsize 5
  grid columnconfigure $d 1 -weight 1
  grid columnconfigure $d 2 -minsize 5


  set j 1
  foreach f $ff {
   label $a.l1$j -text $f -width 12 -anchor w 
   label $a.l2$j -text $info($f,type) -width 5 -anchor w
   label $a.l3$j -text $info($f,size) -width 10 -anchor w
   grid $a.l1$j x $a.l2$j x $a.l3$j -sticky w
   grid rowconfigure $a $j -weight 1
   incr j
  }
  grid columnconfigure $a 0 -weight 1
  grid columnconfigure $a 1 -minsize 5
  grid columnconfigure $a 2 -weight 1
  grid columnconfigure $a 3 -minsize 5
  grid columnconfigure $a 4  -weight 1

  set maxw 0; set maxh 0
  foreach x [$w.b pages] {
   $w.b select $x
   update idletasks
   if {[winfo reqwidth $w]>$maxw} {set maxw [winfo reqwidth $w]}
   if {[winfo reqheight $w]>$maxh} {set maxh [winfo reqheight $w]}
  }
  $w.b select [lindex [$w.b pages] 0]
  wm minsize $w $maxw $maxh

  wm title $w "About: [file tail $file]"
  wm transient $w .
  wm deiconify $w
  wm resizable $w 0 0
  return $w
 }

}


# Import the bsync functions out of their namespace so that we can properly
# provide them as functions.  As jacques@deVilliers.com puts it:
#
# bad bad bad, but it has to be done.

namespace import ::bsync::*
