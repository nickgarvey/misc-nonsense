; Linux: https://gist.github.com/tanyuan/55bca522bf50363ae4573d4bdcf06e2e

SetCapsLockState Off

*CapsLock::
	Send {LControl down}
	Return
*CapsLock up::
	Send {LControl Up}
	; Disable in SC2 because I keep bumping it and cancelling things
	if (A_PriorKey=="CapsLock" && !WinActive("ahk_exe SC2_x64.exe")){
		Suspend On
		Send, {Esc}
		Suspend Off
	}
	Return

