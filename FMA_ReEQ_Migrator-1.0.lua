-- @description FMA ReEQ Migrator: migrates projects from Sai'ke's original ReEQ to ReEQ - FMA Edition
-- @version 1.0
-- @author Free Mix Audio
-- @changelog
--   Initial ReaPack release (same script delivered 2026-10-23; migrates .rpp, .RfxChain and .RTrackTemplate files, writing backup + migrated copies without touching the original)
-- @about
--   Migrates every instance of Sai'ke's original ReEQ in REAPER project files to ReEQ - FMA Edition, keeping every setting. For each file it writes a byte-exact backup and a migrated copy, never overwriting. Full guide travels in the share package.

-- FMA ReEQ Migrator
-- Replaces every instance of Sai'ke's original ReEQ (ReEQ.jsfx) in REAPER
-- project files with ReEQ - FMA Edition (reeq-fma-edition.jsfx), keeping
-- every setting: the whole FX state (sliders + serialized band data) is
-- carried over untouched; only the effect's file reference changes.
--
-- For each processed file "Name.rpp" the script writes, next to it:
--   "Name - backup.rpp"    byte copy of the original (safety net)
--   "Name - migrated.rpp"  the migrated project
-- If a target already exists, a timestamped variant is written instead, so
-- nothing is ever overwritten. The original file is NEVER modified.
-- Batch mode also migrates .RfxChain and .RTrackTemplate files.
--
-- (c) 2026 Free Mix Audio. Free to use and share.

local SRC_BASENAME = "reeq.jsfx"              -- original file (any folder)
local DST_PATH     = "reeq-fma-edition.jsfx"  -- FMA Edition, Effects root

local function log(msg)
  reaper.ShowConsoleMsg(msg .. "\n")
end

local function basename(path)
  return (path:match("([^/\\]+)$") or path)
end

local function split_path(full)
  local dir, file = full:match("^(.*[/\\])([^/\\]+)$")
  if not dir then dir, file = "", full end
  local stem, ext = file:match("^(.*)(%.[^%.]+)$")
  if not stem then stem, ext = file, "" end
  return dir, stem, ext
end

local function file_exists(path)
  local f = io.open(path, "rb")
  if f then f:close() return true end
  return false
end

local function read_all(path)
  local f = io.open(path, "rb")
  if not f then return nil end
  local data = f:read("*a")
  f:close()
  return data
end

local function write_all(path, data)
  local f = io.open(path, "wb")
  if not f then return false end
  f:write(data)
  f:close()
  return true
end

-- Finds a free output name: preferred, else "preferred (timestamp)".
local function free_name(preferred)
  if not file_exists(preferred) then return preferred end
  local dir, stem, ext = split_path(preferred)
  local stamped = dir .. stem .. " (" .. os.date("%Y%m%d-%H%M%S") .. ")" .. ext
  if not file_exists(stamped) then return stamped end
  local n = 2
  while file_exists(dir .. stem .. " (" .. os.date("%Y%m%d-%H%M%S") .. "-" .. n .. ")" .. ext) do
    n = n + 1
  end
  return dir .. stem .. " (" .. os.date("%Y%m%d-%H%M%S") .. "-" .. n .. ")" .. ext
end

-- Rewrites the <JS ...> header lines of original-ReEQ chunks.
-- Processes the content line by line, preserving every byte outside the
-- effect path token (values, JS_SER blob, line endings, everything).
-- Returns new content (or original) and the number of instances replaced.
local function migrate_content(data)
  local out = {}
  local count = 0
  local pos = 1
  local len = #data
  while pos <= len do
    local nl = data:find("\n", pos, true)
    local line, nextpos
    if nl then line = data:sub(pos, nl) nextpos = nl + 1
    else line = data:sub(pos) nextpos = len + 1 end

    -- A JS chunk header looks like:  <JS path "alias"   (path may be quoted).
    -- `line` includes its trailing "\n" when one exists; the tail capture
    -- carries everything after the path token (alias, "\r\n"...) verbatim.
    local indent, sep, rest = line:match("^(%s*)<JS(%s+)(.*)$")
    if indent and rest then
      local token, tail
      if rest:sub(1, 1) == '"' then
        local close = rest:find('"', 2, true)
        if close then token = rest:sub(2, close - 1) tail = rest:sub(close + 1) end
      else
        local sp = rest:find("%s")
        if sp then token = rest:sub(1, sp - 1) tail = rest:sub(sp)
        else token = rest:gsub("%s+$", "") tail = "" end
      end
      if token and basename(token):lower() == SRC_BASENAME then
        line = indent .. "<JS" .. sep .. DST_PATH .. (tail or "")
        count = count + 1
      end
    end
    out[#out + 1] = line
    pos = nextpos
  end
  return table.concat(out), count
end

-- Migrates one file. Returns instances, backup_path, migrated_path, err.
local function migrate_file(path)
  local data = read_all(path)
  if not data then return nil, nil, nil, "no se pudo leer" end
  local migrated, count = migrate_content(data)
  if count == 0 then return 0, nil, nil, nil end

  local dir, stem, ext = split_path(path)
  local backup = free_name(dir .. stem .. " - backup" .. ext)
  if not write_all(backup, data) then
    return nil, nil, nil, "no se pudo escribir el backup"
  end
  local target = free_name(dir .. stem .. " - migrated" .. ext)
  if not write_all(target, migrated) then
    return nil, nil, nil, "no se pudo escribir el archivo migrado"
  end
  return count, backup, target, nil
end

local function is_migratable(path)
  local lower = path:lower()
  if lower:match("%- migrated") or lower:match("%- backup") then
    return false -- never re-process our own outputs
  end
  return lower:match("%.rpp$") ~= nil
      or lower:match("%.rfxchain$") ~= nil
      or lower:match("%.rtracktemplate$") ~= nil
end

local function scan_folder(dir, acc)
  dir = dir:gsub("[/\\]+$", "")
  local i = 0
  while true do
    local file = reaper.EnumerateFiles(dir, i)
    if not file then break end
    local full = dir .. "/" .. file
    if is_migratable(full) then acc[#acc + 1] = full end
    i = i + 1
  end
  local j = 0
  while true do
    local sub = reaper.EnumerateSubdirectories(dir, j)
    if not sub then break end
    scan_folder(dir .. "/" .. sub, acc)
    j = j + 1
  end
end

local function report_file(path, count, backup, target, err)
  if err then
    log("  ERROR en " .. path .. ": " .. err)
  elseif count == 0 then
    log("  Sin ReEQ original: " .. path)
  else
    log("  " .. path)
    log("    instancias migradas: " .. count)
    log("    backup:   " .. tostring(backup))
    log("    migrado:  " .. tostring(target))
  end
end

local function main()
  reaper.ClearConsole()
  log("=== FMA ReEQ Migrator ===")

  local proj, projpath = reaper.EnumProjects(-1)
  local has_saved_project = proj and projpath and projpath ~= ""

  local mode = nil
  if has_saved_project then
    local ret = reaper.MB(
      "Se detectó un proyecto abierto:\n" .. projpath ..
      "\n\nSÍ = migrar ESTE proyecto\nNO = migrar una CARPETA de proyectos",
      "FMA ReEQ Migrator", 4)
    mode = (ret == 6) and "project" or "folder"
  else
    mode = "folder"
  end

  if mode == "project" then
    -- Make sure the file on disk is the current state of the project.
    if reaper.IsProjectDirty(proj) then
      local ret = reaper.MB(
        "El proyecto tiene cambios sin guardar.\n¿Guardarlo y migrar la versión guardada?",
        "FMA ReEQ Migrator", 4)
      if ret ~= 6 then log("Cancelado por el usuario.") return end
      reaper.Main_SaveProject(proj, false)
    end
    local count, backup, target, err = migrate_file(projpath)
    report_file(projpath, count, backup, target, err)
    if err then
      reaper.MB("Error: " .. err, "FMA ReEQ Migrator", 0)
    elseif count == 0 then
      reaper.MB("Este proyecto no contiene instancias del ReEQ original. No se creó ningún archivo.",
        "FMA ReEQ Migrator", 0)
    else
      local ret = reaper.MB(
        "Migración completa: " .. count .. " instancia(s).\n\nBackup:\n" .. backup ..
        "\n\nProyecto migrado:\n" .. target .. "\n\n¿Abrir ahora el proyecto migrado?",
        "FMA ReEQ Migrator", 4)
      if ret == 6 then reaper.Main_openProject(target) end
    end
  else
    local defdir = ""
    if has_saved_project then
      local d = split_path(projpath)
      defdir = d
    end
    local ok, vals = reaper.GetUserInputs("FMA ReEQ Migrator", 1,
      "Carpeta con proyectos:,extrawidth=160", defdir)
    if not ok or not vals or vals == "" then log("Cancelado.") return end
    local folder = vals:match("^[^,]+") or vals
    local files = {}
    scan_folder(folder, files)
    log("Archivos candidatos: " .. #files)
    local total_inst, done, skipped = 0, 0, 0
    for _, f in ipairs(files) do
      local count, backup, target, err = migrate_file(f)
      report_file(f, count, backup, target, err)
      if err then skipped = skipped + 1
      elseif count and count > 0 then done = done + 1 total_inst = total_inst + count
      end
    end
    reaper.MB("Modo carpeta terminado.\n\nArchivos migrados: " .. done ..
      "\nInstancias totales: " .. total_inst ..
      "\nCon error: " .. skipped ..
      "\n\nDetalle completo en la consola (Actions > Show console).",
      "FMA ReEQ Migrator", 0)
  end
  log("=== Fin ===")
end

main()
