import './style.css';
import { api, ApiError, hasSession, setToken, type Task, type User } from './api';

type Filter = 'all' | 'pending' | 'done';
const root = document.querySelector<HTMLDivElement>('#app')!;
let user: User | null = null;
let tasks: Task[] = [];
let filter: Filter = 'all';
let search = '';
let authMode: 'login' | 'register' = 'login';
let toastTimer: ReturnType<typeof setTimeout>;
const busy = new Set<number>();

const escape = (text: string): string => text.replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]!));
const paths: Record<string, string> = {
  grid: '<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
  circle: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/>',
  arrow: '<path d="M5 12h14m-6-6 6 6-6 6"/>',
  edit: '<path d="m16 3 5 5L9 20l-6 1 1-6Z"/><path d="m13 6 5 5"/>',
  trash: '<path d="M3 6h18M9 6V3h6v3M5 6l1 15h12l1-15M10 10v7M14 10v7"/>',
  close: '<path d="m6 6 12 12M6 18 18 6"/>',
  logout: '<path d="M9 4H4v16h5M9 12h12m-4-4 4 4-4 4"/>',
  spark: '<path d="m12 2 2.5 7.5L22 12l-7.5 2.5L12 22l-2.5-7.5L2 12l7.5-2.5Z"/>',
};
const icon = (name: string): string => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name] ?? paths.grid}</svg>`;
const brand = `<div class="brand"><span class="brand-mark">${icon('spark')}</span>fluxo<span class="brand-dot">.</span></div>`;

function toast(message: string): void {
  const el = document.querySelector<HTMLDivElement>('#toast')!;
  clearTimeout(toastTimer);
  el.textContent = message;
  el.classList.add('visible');
  toastTimer = setTimeout(() => el.classList.remove('visible'), 4500);
}

function handleError(error: unknown): void {
  if (error instanceof ApiError && error.status === 401 && user) {
    logout();
    toast('Sua sessão expirou. Entre novamente.');
  } else toast(error instanceof Error ? error.message : 'Algo deu errado. Tente novamente.');
}

function logout(): void {
  setToken(null);
  user = null;
  tasks = [];
  search = '';
  filter = 'all';
  document.querySelectorAll('dialog').forEach(dialog => dialog.remove());
  renderAuth();
}

function renderAuth(): void {
  const register = authMode === 'register';
  root.innerHTML = `<main class="auth-shell">
    <section class="auth-story">${brand}<div class="story-copy"><span class="eyebrow">MENOS RUÍDO. MAIS ESPAÇO.</span><h1>Um passo.<br>Uma tarefa.<br><span>Seu ritmo.</span></h1><p>Organize o que importa e abra espaço<br>para o que vem depois.</p></div>
    <div class="orbit-art" aria-hidden="true"><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><div class="floating-note note-one">${icon('check')} Fazer acontecer</div><div class="floating-note note-two">${icon('spark')} Sem pressa. Com foco.</div><div class="art-dot"></div></div>
    <span class="story-footer">UM POUCO DE ORGANIZAÇÃO, UM NOVO FLUXO.</span></section>
    <section class="auth-panel"><div class="auth-card enter"><span class="mini-label">SEU ESPAÇO PESSOAL</span><h2>${register ? 'Comece seu fluxo.' : 'Que bom ter você aqui.'}</h2><p>${register ? 'Crie uma conta e tire as ideias do papel.' : 'Entre para continuar de onde parou.'}</p>
    <div class="auth-tabs"><button type="button" data-mode="login" class="${!register ? 'active' : ''}">Entrar</button><button type="button" data-mode="register" class="${register ? 'active' : ''}">Criar conta</button></div>
    <form id="auth-form">${register ? '<label>Seu nome<input name="username" required maxlength="70" autocomplete="username" placeholder="Como podemos te chamar?"></label>' : ''}<label>Email<input name="email" type="email" required maxlength="255" autocomplete="email" placeholder="voce@exemplo.com"></label><label>Senha<input name="password" type="password" required ${register ? 'minlength="8" maxlength="128" autocomplete="new-password" placeholder="Pelo menos 8 caracteres"' : 'autocomplete="current-password" placeholder="Sua senha"'}></label><p class="form-error" id="auth-error" role="alert"></p><button class="button primary full" type="submit">${register ? 'Criar minha conta' : 'Entrar no meu espaço'}${icon('arrow')}</button></form><div class="auth-footnote">${icon('circle')} Um lugar simples para suas próximas conquistas.</div></div></section></main>`;
  root.querySelectorAll<HTMLButtonElement>('[data-mode]').forEach(button => button.addEventListener('click', () => { authMode = button.dataset.mode as typeof authMode; renderAuth(); }));
  root.querySelector<HTMLFormElement>('#auth-form')!.addEventListener('submit', async event => {
    event.preventDefault();
    const form = event.currentTarget as HTMLFormElement;
    const button = form.querySelector<HTMLButtonElement>('button[type=submit]')!;
    const errorEl = form.querySelector<HTMLElement>('#auth-error')!;
    const data = new FormData(form);
    button.disabled = true;
    button.textContent = 'Só um instante…';
    errorEl.textContent = '';
    try {
      const email = String(data.get('email')).trim();
      const password = String(data.get('password'));
      if (register) {
        await api.register(String(data.get('username')).trim(), email, password);
        authMode = 'login';
        renderAuth();
        root.querySelector<HTMLInputElement>('[name=email]')!.value = email;
        toast('Conta criada! Entre com seu email e senha.');
        return;
      }
      await api.login(email, password);
      const account = await api.me();
      tasks = await api.tasks();
      user = account;
      renderDashboard();
    } catch (error) {
      if (!user) setToken(null);
      errorEl.textContent = error instanceof Error ? error.message : 'Não foi possível entrar.';
    } finally {
      button.disabled = false;
      button.innerHTML = `${register ? 'Criar minha conta' : 'Entrar no meu espaço'}${icon('arrow')}`;
    }
  });
}

function renderDashboard(): void {
  root.innerHTML = `<div class="app-shell enter"><aside class="sidebar">${brand}<span class="nav-label">MEU ESPAÇO</span><nav aria-label="Filtros de tarefas">${(['all', 'pending', 'done'] as Filter[]).map((value, i) => `<button class="nav-item" data-filter="${value}">${icon(['grid', 'circle', 'check'][i])}<span>${['Todas as tarefas', 'Em andamento', 'Concluídas'][i]}</span><span class="nav-count" id="count-${value}"></span></button>`).join('')}</nav><div class="sidebar-tip">${icon('spark')}<p>Pequenos passos.<br><strong>Grandes movimentos.</strong></p><span>Uma tarefa de cada vez.</span></div><div class="profile"><span class="avatar">${escape(user!.username.slice(0, 1).toUpperCase())}</span><div><strong>${escape(user!.username)}</strong><span>Seu espaço pessoal</span></div><button class="icon-button" id="logout" aria-label="Sair da conta" title="Sair">${icon('logout')}</button></div></aside>
    <main class="workspace"><header class="topbar"><span class="breadcrumb">Meu espaço <span>/</span> <strong>Tarefas</strong></span><span class="date">${new Intl.DateTimeFormat('pt-BR', { day: 'numeric', month: 'long' }).format(new Date())}</span></header>
    <div class="content"><section class="page-heading"><div><span class="eyebrow">UM NOVO DIA, NOVAS POSSIBILIDADES</span><h1>Encontre seu fluxo<span>.</span></h1><p>Organize suas ideias. Faça espaço para acontecer.</p></div><button class="button primary" id="new-task">${icon('plus')} Nova tarefa</button></section>
    <section class="hero"><div><span class="hero-label">NO SEU RITMO</span><h2>Cada passo conta.</h2><p id="progress-copy"></p><div class="progress-track"><span id="progress-bar"></span></div><span class="progress-caption" id="progress-caption"></span></div><div class="hero-art" aria-hidden="true"><div class="petal p1"></div><div class="petal p2"></div><div class="petal p3"></div><div class="petal p4"></div><div class="petal-center">${icon('spark')}</div></div><span class="hero-number" id="progress-number"></span></section>
    <section class="task-section" aria-labelledby="list-title"><div class="list-heading"><div><h2 id="list-title">Suas tarefas <span id="visible-count"></span></h2><p>O próximo passo começa aqui.</p></div><label class="search-box">${icon('search')}<input id="search" type="search" aria-label="Buscar tarefas" placeholder="Buscar uma tarefa…" maxlength="150"></label></div><div class="filter-tabs" role="group" aria-label="Filtrar tarefas"><button data-filter="all">Todas</button><button data-filter="pending">Em andamento</button><button data-filter="done">Concluídas</button></div><div id="task-list" aria-live="polite"></div></section><footer class="workspace-footer"><span>Feito para simplificar seu dia.</span><span>menos pressa, mais fluxo ${icon('spark')}</span></footer></div></main></div>`;
  root.querySelector('#logout')!.addEventListener('click', logout);
  root.querySelector('#new-task')!.addEventListener('click', () => openEditor());
  root.querySelectorAll<HTMLButtonElement>('[data-filter]').forEach(button => button.addEventListener('click', () => { filter = button.dataset.filter as Filter; renderTasks(); }));
  const input = root.querySelector<HTMLInputElement>('#search')!;
  input.value = search;
  input.addEventListener('input', () => { search = input.value; renderTasks(); });
  root.querySelector('#task-list')!.addEventListener('click', async event => {
    const button = (event.target as Element).closest<HTMLButtonElement>('button[data-action]');
    if (!button) return;
    const task = tasks.find(item => item.id === Number(button.dataset.id));
    if (!task || busy.has(task.id)) return;
    if (button.dataset.action === 'edit') openEditor(task);
    else if (button.dataset.action === 'delete') openDelete(task);
    else {
      busy.add(task.id);
      renderTasks();
      try {
        const updated = await api.update(task.id, { concluida: !task.concluida });
        tasks = tasks.map(item => item.id === updated.id ? updated : item);
        toast(updated.concluida ? 'Mais um passo concluído. Boa!' : 'Tarefa movida para em andamento.');
      } catch (error) { handleError(error); }
      finally { busy.delete(task.id); if (user) renderTasks(); }
    }
  });
  renderTasks();
}

function renderTasks(): void {
  const done = tasks.filter(task => task.concluida).length;
  const progress = tasks.length ? Math.round(done / tasks.length * 100) : 0;
  const visible = tasks.filter(task => (filter === 'all' || task.concluida === (filter === 'done')) && `${task.title} ${task.descricao ?? ''}`.toLocaleLowerCase('pt-BR').includes(search.toLocaleLowerCase('pt-BR'))).sort((a, b) => Number(a.concluida) - Number(b.concluida) || b.id - a.id);
  const counts = { all: tasks.length, pending: tasks.length - done, done };
  root.querySelectorAll<HTMLButtonElement>('[data-filter]').forEach(button => { const active = button.dataset.filter === filter; button.classList.toggle('active', active); button.setAttribute('aria-pressed', String(active)); });
  for (const key of Object.keys(counts) as Filter[]) root.querySelector(`#count-${key}`)!.textContent = String(counts[key]);
  root.querySelector('#progress-copy')!.textContent = tasks.length ? `${done} de ${tasks.length} tarefas concluídas. ${progress === 100 ? 'Tudo em dia. Aproveite a pausa!' : 'Você está construindo seu caminho.'}` : 'Tire uma ideia do papel. Sua primeira tarefa pode começar agora.';
  (root.querySelector('#progress-bar') as HTMLElement).style.width = `${progress}%`;
  root.querySelector('#progress-caption')!.textContent = `${progress}% do seu caminho concluído`;
  root.querySelector('#progress-number')!.textContent = `${progress}%`;
  root.querySelector('#visible-count')!.textContent = String(visible.length);
  root.querySelector('#task-list')!.innerHTML = visible.length ? `<div class="task-grid">${visible.map((task, index) => `<article class="task-card ${task.concluida ? 'is-done' : ''}" style="--delay:${Math.min(index, 8) * 35}ms"><div class="card-top"><span class="task-status ${task.concluida ? 'done' : ''}"><span></span>${task.concluida ? 'Concluída' : 'Em andamento'}</span><div class="card-actions"><button class="icon-button" data-action="edit" data-id="${task.id}" aria-label="Editar ${escape(task.title)}" ${busy.has(task.id) ? 'disabled' : ''}>${icon('edit')}</button><button class="icon-button danger-hover" data-action="delete" data-id="${task.id}" aria-label="Excluir ${escape(task.title)}" ${busy.has(task.id) ? 'disabled' : ''}>${icon('trash')}</button></div></div><h3>${escape(task.title)}</h3><p class="task-description">${task.descricao ? escape(task.descricao) : '<span class="muted-description">Um pequeno passo na direção certa.</span>'}</p><div class="card-bottom"><span class="task-id">TAREFA ${String(task.id).padStart(3, '0')}</span><button class="complete-button ${task.concluida ? 'checked' : ''}" data-action="toggle" data-id="${task.id}" aria-label="${task.concluida ? 'Reabrir' : 'Concluir'} ${escape(task.title)}" aria-pressed="${task.concluida}" ${busy.has(task.id) ? 'disabled' : ''}>${busy.has(task.id) ? '<span class="spinner"></span>' : icon('check')}<span>${task.concluida ? 'Feito' : 'Concluir'}</span></button></div></article>`).join('')}</div>` : `<div class="empty-state"><span class="empty-icon">${icon(search ? 'search' : 'spark')}</span><h3>${search ? 'Nenhuma tarefa por aqui.' : filter === 'done' ? 'As conquistas vêm com o tempo.' : filter === 'pending' && tasks.length ? 'Tudo em dia!' : 'Abra espaço para sua primeira ideia.'}</h3><p>${search ? 'Experimente buscar por outra palavra.' : filter === 'done' ? 'Suas tarefas concluídas aparecerão aqui.' : 'Uma tarefa simples já é um ótimo começo.'}</p>${!search && filter !== 'done' ? `<button class="button secondary" id="empty-create">${icon('plus')} Criar uma tarefa</button>` : ''}</div>`;
  root.querySelector('#empty-create')?.addEventListener('click', () => openEditor());
}

function showDialog(html: string, className: string): HTMLDialogElement {
  const dialog = document.createElement('dialog');
  dialog.className = className;
  dialog.innerHTML = html;
  dialog.setAttribute('aria-labelledby', 'dialog-title');
  document.body.append(dialog);
  dialog.querySelectorAll('[data-close]').forEach(button => button.addEventListener('click', () => dialog.close()));
  dialog.addEventListener('click', event => { if (event.target === dialog) { const rect = dialog.getBoundingClientRect(); if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close(); } });
  dialog.addEventListener('close', () => dialog.remove(), { once: true });
  dialog.showModal();
  return dialog;
}

function openEditor(task?: Task): void {
  const dialog = showDialog(`<div class="drawer-header"><span class="mini-label">UM PASSO DE CADA VEZ</span><button class="icon-button" data-close aria-label="Fechar painel">${icon('close')}</button></div><h2 id="dialog-title">${task ? 'Ajuste seu próximo passo.' : 'O que vamos fazer?'}</h2><p class="drawer-intro">${task ? 'As ideias mudam. Suas tarefas também podem.' : 'Dê um nome à ideia. O resto vem no seu ritmo.'}</p><form id="task-form"><label>Título <span class="required">*</span><input name="title" required maxlength="150" placeholder="Ex.: organizar a semana" value="${escape(task?.title ?? '')}"></label><label>Descrição <span class="optional">opcional</span><textarea name="descricao" maxlength="350" rows="5" placeholder="Algum detalhe para lembrar depois?">${escape(task?.descricao ?? '')}</textarea><span class="character-count"><span id="char-count">${task?.descricao?.length ?? 0}</span>/350</span></label><label class="checkbox-label"><input type="checkbox" name="concluida" ${task?.concluida ? 'checked' : ''}>Essa tarefa já está concluída</label><p class="form-error" id="task-error" role="alert"></p><div class="drawer-footer"><button class="button secondary" type="button" data-close>Cancelar</button><button class="button primary" type="submit">${task ? 'Salvar alterações' : 'Criar tarefa'}${icon('arrow')}</button></div></form><div class="drawer-decoration" aria-hidden="true">${icon('spark')}</div>`, 'task-drawer');
  const form = dialog.querySelector<HTMLFormElement>('form')!;
  form.querySelector<HTMLTextAreaElement>('textarea')!.addEventListener('input', event => { dialog.querySelector('#char-count')!.textContent = String((event.target as HTMLTextAreaElement).value.length); });
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const data = new FormData(form);
    const title = String(data.get('title')).trim();
    const errorEl = dialog.querySelector<HTMLElement>('#task-error')!;
    if (!title) { errorEl.textContent = 'Dê um título à sua tarefa.'; return; }
    const button = form.querySelector<HTMLButtonElement>('button[type=submit]')!;
    button.disabled = true;
    button.textContent = 'Salvando…';
    errorEl.textContent = '';
    const input = { title, descricao: String(data.get('descricao')).trim() || null, concluida: data.has('concluida') };
    try {
      const saved = task ? await api.update(task.id, input) : await api.create(input);
      tasks = task ? tasks.map(item => item.id === saved.id ? saved : item) : [...tasks, saved];
      dialog.close();
      renderTasks();
      toast(task ? 'Tarefa atualizada.' : 'Uma nova ideia ganhou espaço.');
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) handleError(error);
      else errorEl.textContent = error instanceof Error ? error.message : 'Não foi possível salvar.';
    } finally { button.disabled = false; button.innerHTML = `${task ? 'Salvar alterações' : 'Criar tarefa'}${icon('arrow')}`; }
  });
}

function openDelete(task: Task): void {
  const dialog = showDialog(`<span class="delete-icon">${icon('trash')}</span><h2 id="dialog-title">Deixar essa tarefa ir?</h2><p>“${escape(task.title)}” será excluída. Essa ação não pode ser desfeita.</p><p id="delete-error" class="form-error" role="alert"></p><div class="delete-actions"><button class="button secondary" data-close>Manter tarefa</button><button class="button danger" id="confirm-delete">Excluir tarefa</button></div>`, 'delete-dialog');
  dialog.querySelector('#confirm-delete')!.addEventListener('click', async event => {
    const button = event.currentTarget as HTMLButtonElement;
    button.disabled = true;
    button.textContent = 'Excluindo…';
    try { await api.remove(task.id); tasks = tasks.filter(item => item.id !== task.id); dialog.close(); renderTasks(); toast('Tarefa excluída. Espaço para o que vem.'); }
    catch (error) { if (error instanceof ApiError && error.status === 401) handleError(error); else dialog.querySelector('#delete-error')!.textContent = error instanceof Error ? error.message : 'Não foi possível excluir.'; }
    finally { button.disabled = false; button.textContent = 'Excluir tarefa'; }
  });
}

async function start(): Promise<void> {
  if (!hasSession()) { renderAuth(); return; }
  root.innerHTML = `<main class="loading-screen">${brand}<span class="spinner"></span><p>Preparando seu espaço…</p></main>`;
  try { user = await api.me(); tasks = await api.tasks(); renderDashboard(); }
  catch (error) {
    if (error instanceof ApiError && error.status === 401) setToken(null);
    user = null;
    renderAuth();
    toast(error instanceof ApiError && error.status === 401 ? 'Entre novamente para continuar.' : error instanceof Error ? error.message : 'Não foi possível carregar.');
  }
}

void start();
