# Configurating streaming behaviour¶

**URL:** https://google.github.io/adk-docs/streaming/configuration/
**Wygenerowano:** 9.06.2025, 22:24:02

---

Configurating streaming behaviour¶ There are some configurations you can set for live(streaming) agents. It's set by RunConfig. You should use RunConfig with your Runner.run_live(...). For example, if you want to set voice config, you can leverage speech_config. voice_config = genai_types.VoiceConfig( prebuilt_voice_config=genai_types.PrebuiltVoiceConfigDict( voice_name='Aoede' ) ) speech_config = genai_types.SpeechConfig(voice_config=voice_config) run_config = RunConfig(speech_config=speech_config) runner.run_live( ..., run_config=run_config, ) var tabs=__md_get("__tabs");if(Array.isArray(tabs))e:for(var set of document.querySelectorAll(".tabbed-set")){var labels=set.querySelector(".tabbed-labels");for(var tab of tabs)for(var label of labels.getElementsByTagName("label"))if(label.innerText.trim()===tab){var input=document.getElementById(label.htmlFor);input.checked=!0;continue e}} var target=document.getElementById(location.hash.slice(1));target&&target.name&&(target.checked=target.name.startsWith("__tabbed_")) Back to top
